"""Native Vercel FastAPI entrypoint; only lightweight inference dependencies."""
import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from retail_mvp.catalogue import NotReady, get_catalogue, safe_url
from retail_mvp.config import Settings
from retail_mvp.groq import factual_reason, generate
from retail_mvp.limits import LimitError, enforce, shared_configured
from retail_mvp.models import ChatRequest, ChatResponse, Reference
from retail_mvp.safety import InvalidPreference, boundary, resolve_request, safe_excerpt

settings = Settings.read()
logger = logging.getLogger('retailassist.mvp')
app = FastAPI(title='RetailAssist Healthy U MVP', version='0.1.0', description='Anonymous catalogue-grounded retail chat. Not medical advice.')

class BodyLimit:
    def __init__(self, app, maximum=24576):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] not in {'POST', 'PUT', 'PATCH'}:
            return await self.app(scope, receive, send)
        chunks = []
        size = 0
        while True:
            event = await receive()
            if event['type'] == 'http.disconnect':
                return
            chunk = event.get('body', b'')
            size += len(chunk)
            if size > self.maximum:
                response = JSONResponse({'error': {'code': 'body_too_large', 'message': 'Request body exceeds the anonymous-chat limit.'}}, status_code=413)
                return await response(scope, receive, send)
            chunks.append(chunk)
            if not event.get('more_body'):
                break
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': b''.join(chunks), 'more_body': False}
            return await receive()
        return await self.app(scope, replay, send)

app.add_middleware(BodyLimit)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.origins), allow_methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'], allow_credentials=False)

@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    return JSONResponse({'error': {'code': 'invalid_request', 'message': 'Check the message length, history and preference values.'}}, status_code=422)

@app.exception_handler(LimitError)
async def limited(request, error):
    message = 'The anonymous request or usage limit was reached. Try again later.' if error.status == 429 else 'Shared abuse protection is not ready. The backend is refusing requests safely.'
    return JSONResponse({'error': {'code': error.code, 'message': message, 'retry_after': error.retry_after}}, status_code=error.status, headers={'Retry-After': str(error.retry_after)})

@app.exception_handler(Exception)
async def unexpected(request, error):
    logger.error('request_failed class=%s', type(error).__name__)
    return JSONResponse({'error': {'code': 'internal_error', 'message': 'The request could not be completed. Please try again.'}}, status_code=500)

def availability():
    try:
        catalogue = get_catalogue()
    except NotReady as error:
        return None, str(error)
    if settings.require_shared and not shared_configured(settings):
        return catalogue, 'shared_limiter_not_configured'
    return catalogue, None

@app.get('/health')
def health():
    return {'status': 'alive', 'service': 'retailassist-mvp'}

@app.get('/ready')
def ready():
    catalogue, reason = availability()
    return JSONResponse({'ready': reason is None, 'reason': reason, 'catalogue_available': catalogue is not None, 'generation_configured': bool(settings.api_key)}, status_code=200 if reason is None else 503)

@app.get('/api/system-info')
def system_info():
    catalogue, reason = availability()
    return {'ready': reason is None, 'reason': reason, 'model': settings.model, 'generation_configured': bool(settings.api_key), 'catalogue_count': len(catalogue.products) if catalogue else 0, 'currency': 'KES', 'retrieval': catalogue.method if catalogue else 'unavailable', 'source_snapshot_date': catalogue.manifest.get('source_snapshot_date') if catalogue else None, 'permission': 'user_approved_presentation_mvp', 'limitations': ['Not an official Healthy U service.', 'Historical snapshot; confirm prices and stock.', 'No clinical advice or efficacy claims.']}

@app.post('/api/chat', response_model=ChatResponse)
@app.post('/api/recommend', response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request):
    request_id = uuid.uuid4().hex
    started = time.monotonic()
    # Vercel overwrites its forwarding header. Local mode uses the actual peer address.
    import os
    identity = (request.headers.get('x-vercel-forwarded-for', '') if os.getenv('VERCEL') else '') or (request.client.host if request.client else 'unknown')
    await enforce(identity.split(',')[0].strip(), settings)
    guarded = boundary(body.message)
    if guarded:
        return ChatResponse(answer=guarded[1], mode=guarded[0], retrieval='not_invoked', preferences=body.preferences, request_id=request_id)
    catalogue, reason = availability()
    if reason:
        return JSONResponse({'error': {'code': reason, 'message': 'The approved catalogue/index or public-request controls are not ready. Run the preparation commands and configure deployment settings.'}}, status_code=503)
    try:
        query, preferences = resolve_request(body)
    except InvalidPreference as error:
        return ChatResponse(answer=str(error), mode='clarification', retrieval='not_invoked', preferences=body.preferences, request_id=request_id)
    # Recheck resolved follow-up context; a prior medical request cannot sneak into retrieval.
    guarded = boundary(query)
    if guarded:
        return ChatResponse(answer=guarded[1], mode=guarded[0], retrieval='not_invoked', preferences=preferences, request_id=request_id)
    products = catalogue.search(query, preferences, body.k)
    notices = ['Listed prices are KES from the approved source snapshot. Current stock and price changes are not confirmed.']
    if not products:
        return ChatResponse(answer='I could not find catalogue records that satisfy all those preferences. Some fields, including ingredients, confirmed dietary labels, brands and stock, are absent from this export; I will not guess them. Try a product name/category and a wider budget.', mode='no_matches', retrieval=catalogue.method, preferences=preferences, notices=notices, request_id=request_id)
    async def reserve(amount):
        await enforce(identity, settings, tokens=amount, request=False)
    try:
        generated = await generate(query, body.history, products, preferences, settings, reserve=reserve)
    except LimitError:
        from retail_mvp.groq import Generation
        generated = Generation('fallback_local_quota', {}, notice='The application token budget is exhausted or its shared counter is unavailable. Further Groq calls were skipped; catalogue facts are shown.')
    references = []
    for p in products:
        reason = generated.reasons.get(p['id']) or factual_reason(p, preferences)
        references.append(Reference(id=p['id'], name=p['name'], description=safe_excerpt(p['description'], 260) or 'Listing text is omitted where it contains health or efficacy claims.', price=p['price'], currency='KES', url=safe_url(p['url']), category=p['category'], stock=p['stock'], source_record_id=p['source_record_id'], reason=reason))
    answer = generated.opening + '\n\n' + '\n\n'.join(f"**{p.name}** [HU:{p.id}]\n\n{p.reason}" for p in references)
    if generated.follow_up:
        answer += '\n\n' + generated.follow_up
    if generated.notice:
        notices.append(generated.notice)
    logger.info('chat_completed id=%s mode=%s references=%d elapsed_ms=%d', request_id, generated.mode, len(references), int((time.monotonic() - started) * 1000))
    return ChatResponse(answer=answer, references=references, mode=generated.mode, retrieval=catalogue.method, preferences=preferences, notices=notices, retry_after=generated.retry_after, request_id=request_id)
