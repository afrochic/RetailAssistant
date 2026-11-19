"""Conservative retail boundary. Clinical decisions are deliberately out of scope."""
import re
from .models import ChatRequest, Preferences

URGENT = re.compile(r'\b(chest pain|difficulty breathing|cannot breathe|can.t breathe|unconscious|seizure|overdose|suicid\w*|worst headache|sudden severe headache|one.sided weakness|severe allergic|anaphylax\w*|stroke)\b', re.I)
MEDICAL = re.compile(r'\b(headaches?|migraines?|pain|symptoms?|diagnos\w*|treat\w*|cur(?:e|es|ing)|medicat\w*|dosage|dose|pregnan\w*|breastfeed\w*|diabet\w*|cancer|depress\w*|anxiety|hypertension|blood pressure|weight loss|lose weight|fertility|insomnia|asthma|eczema|psoriasis|copd|adhd|pcos|osteoporosis|anemia|anaemia|ibs|ibd|cholesterol|blood sugar|insulin|infection|fever|nausea|vomit\w*|allerg\w*|intoleran\w*|epilepsy|arthritis|thyroid|kidney|liver disease|drug interaction|children|toddler|infant)\b', re.I)
INJECTION = re.compile(r'ignore (?:all |previous |the )?(?:instructions|rules)|system prompt|api.?key|reveal.{0,15}(secret|password)|invent.{0,15}product|bypass.{0,15}(safety|budget|rules)', re.I)
CLAIMS = re.compile(r'\b(cure\w*|treat\w*|prevent\w*|diagnos\w*|heal\w*|clinically|medicin\w*|therapeut\w*|guarantee\w*|reduce\w* (?:pain|anxiety|blood)|relie\w*|dosage|dose|detox\w*|weight.loss)\b', re.I)

class InvalidPreference(ValueError):
    pass

def boundary(message: str) -> tuple[str, str] | None:
    visual_headache = (re.search(r'\bsevere headache\b', message, re.I)
                       and re.search(r'\b(?:blurred vision|vision loss|loss of vision)\b', message, re.I))
    if URGENT.search(message) or visual_headache:
        return ('urgent_safety', 'This could need urgent medical attention. Please contact local emergency services or seek urgent care now. I cannot assess symptoms or recommend retail products as treatment.')
    if MEDICAL.search(message) or re.search(r'\b(?:supplement|vitamin|herb|product)\w*\s+(?:that\s+)?(?:helps?|treats?|cures?|relieves?|prevents?)\b', message, re.I):
        return ('medical_boundary', 'I can help compare catalogue products, but I cannot diagnose symptoms or recommend medicines or supplements to treat a medical concern. Please speak with a qualified healthcare professional, especially if symptoms are new, severe or persistent. For ordinary shopping, you can ask for a product category and budget.')
    if INJECTION.search(message):
        return ('safety_refusal', 'I can help with catalogue-grounded shopping requests, but I cannot reveal secrets, invent products or bypass safety and budget limits.')
    return None

def redact(text: str) -> str:
    text = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[email removed]', text)
    return re.sub(r'(?<!\d)(?:\+?254|0)[17]\d{8}(?!\d)', '[phone removed]', text)

def safe_excerpt(text: str, limit: int = 400) -> str:
    chunks = re.split(r'(?<=[.!?])\s+|\n+', text)
    safe = [s for s in chunks if not CLAIMS.search(s) and not INJECTION.search(s)]
    return ' '.join(safe)[:limit].strip()

def resolve_request(req: ChatRequest) -> tuple[str, Preferences]:
    text = req.message.strip()
    if re.search(r'\b(?:USD|INR|EUR|dollars|rupees)\b', text, re.I):
        raise InvalidPreference('This approved catalogue uses KES. Please give your budget in KES or KSh.')
    # Unknown negative/dietary requirements are not silently dropped.
    for exclusion in re.finditer(r"\b(?:without|exclude|avoid|free of|no|don.t want|do not include)\s+(.+?)(?=\s+(?:and|or)\b|[,;.!?]|$)", text, re.I):
        tail = exclusion[1]
        if re.match(r'more than\s+\d', tail, re.I):
            continue
        if not re.match(r'(?:nuts?|peanuts?|dairy|milk|soy|gluten|wheat|sesame|eggs?|sugar|caffeine|gelatin|lactose|alcohol)\b', tail, re.I):
            raise InvalidPreference('I cannot reliably verify that exclusion from this export. Please check the manufacturer ingredient information or use a product/category and KES budget request.')
    known_free = r'(?:gluten|nut|peanut|dairy|soy|wheat|lactose|sugar|caffeine)[- ]free'
    if re.search(r'\b[a-z]+[- ]free\b', text, re.I) and not re.search(known_free, text, re.I):
        raise InvalidPreference('That free-from requirement is not a verified field in this export. I will not guess it from marketing text.')
    values = req.preferences.model_dump()
    # Explicit preferences (including an empty reset) are authoritative. When
    # an API client supplies only history, re-derive its prior hard constraints.
    if 'preferences' not in req.model_fields_set:
        for turn in req.history:
            if turn.role == 'user' and not boundary(turn.content):
                try:
                    _, prior = resolve_request(ChatRequest(message=turn.content, preferences=Preferences(**values)))
                    values = prior.model_dump()
                except InvalidPreference:
                    continue
    patterns = [('max_price', r'\b(?:under|below|up to|at most|no more than|budget(?: of)?)\s*(?:KES|KShs?|shillings)?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?'), ('min_price', r'\b(?:above|at least|over)\s*(?:KES|KShs?)?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?')]
    for field, pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            values[field] = float(match[1].replace(',', '')) * (1000 if match[2] else 1)
    for match in re.findall(r'\b(?:without|exclude|avoid|allergic to|free of|no)\s+(nuts?|peanuts?|dairy|milk|soy|gluten|wheat|sesame|eggs?|sugar|caffeine|gelatin|lactose|alcohol)\b', text, re.I):
        if match.casefold() not in values['excluded_ingredients']:
            values['excluded_ingredients'].append(match.casefold())
    for label in re.findall(r'\b(gluten[- ]free|nut[- ]free|peanut[- ]free|dairy[- ]free|soy[- ]free|wheat[- ]free|lactose[- ]free|vegan|vegetarian|halal|kosher|sugar[- ]free|caffeine[- ]free)\b', text, re.I):
        normalized = label.lower().replace('-', ' ')
        if normalized not in values['required_labels']:
            values['required_labels'].append(normalized)
    brand = re.search(r'\bbrand\s+([A-Za-z][A-Za-z -]{1,35}?)(?=\s+(?:under|below|for|with)|$)', text, re.I)
    if brand:
        values['brand'] = brand[1].strip()
    if re.search(r'\bin.stock\b', text, re.I):
        values['in_stock'] = True
    query = text
    if re.match(r'^(?:please\s+)?(?:cheaper|under|below|only|what about|how about|show more|any others|compare|and )', text, re.I):
        prior = next((turn.content for turn in reversed(req.history) if turn.role == 'user' and not boundary(turn.content) and len(tokens_for_intent(turn.content)) > 1), '')
        if prior:
            new_subject = re.sub(r'^(?:please\s+)?(?:what about|how about)\s+', '', text, flags=re.I)
            if new_subject != text and any(not word.isdigit() and word not in {'kes', 'ksh', 'kshs'} for word in tokens_for_intent(new_subject)):
                query = new_subject
            else:
                query = re.sub(patterns[0][1], '', prior, flags=re.I) + ' ' + text
    try:
        return query[:1600], Preferences(**values)
    except ValueError:
        raise InvalidPreference('Those preferences conflict. Please check the minimum and maximum budget.') from None

def tokens_for_intent(text: str) -> list[str]:
    from .catalogue import tokens
    return tokens(text)
