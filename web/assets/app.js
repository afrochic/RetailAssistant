'use strict';
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = value => Number(value).toLocaleString('en-IN', {maximumFractionDigits: 2});
const safeURL = value => { try { const url = new URL(value); return ['https:', 'http:'].includes(url.protocol) ? url.href.replace(/^http:/, 'https:') : ''; } catch { return ''; } };
const imageURL = value => { try { const url = new URL(value); return url.protocol === 'https:' && url.hostname === 'rukminim2.flixcart.com' ? url.href : ''; } catch { return ''; } };
const STORAGE_KEY = 'retailassist.shortlist.v1';
let saved = [];
try { const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); if (Array.isArray(stored)) saved = stored.filter(p => p && typeof p.id === 'string' && typeof p.name === 'string' && Number.isFinite(p.price)).slice(0, 100); } catch { /* Private browsing/storage restrictions must not stop discovery. */ }
const state = {products: [], query: '', constraints: {}, semantic: true, controller: null, detailController: null, detailId: null};
let toastTimer;
function toast(message) { const el = $('#toast'); el.textContent = message; el.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('visible'), 2700); }
function persist() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(saved)); } catch { toast('Saved for this visit. Your browser couldn’t keep these items after closing.'); } }
function isSaved(id) { return saved.some(p => p.id === id); }
function updateSaveButtons() {
  $('#shortlist-count').textContent = saved.length;
  $('#shortlist-button').setAttribute('aria-label', `Open your shortlist, ${saved.length} saved ${saved.length === 1 ? 'item' : 'items'}`);
  $$('.save-button').forEach(b => { const active = isSaved(b.dataset.id); b.classList.toggle('saved', active); b.setAttribute('aria-pressed', String(active)); b.setAttribute('aria-label', `${active ? 'Remove' : 'Save'} ${b.dataset.name}`); });
  $$('.detail-save').forEach(b => { const active = isSaved(b.dataset.id); b.innerHTML = `${icon('heart')} ${active ? 'Saved to shortlist' : 'Save for later'}`; b.setAttribute('aria-pressed', String(active)); });
}
function toggleSave(product) {
  const active = isSaved(product.id);
  if (active) saved = saved.filter(p => p.id !== product.id);
  else { if (saved.length >= 100) { toast('Your shortlist is full. Remove an item to make room.'); return; } saved.push(product); }
  persist(); updateSaveButtons(); renderShortlist(); toast(active ? 'Removed from your shortlist' : 'A good find, saved for later.');
}
const categoryLabel = category => ({'Mobiles & Accessories':'TECH & AUDIO','Computers':'TECH & AUDIO','Footwear':'ON THE MOVE','Home Decor & Festive Needs':'AT HOME','Home Furnishing':'AT HOME','Kitchen & Dining':'EVERYDAY LIVING','Bags, Wallets & Belts':'TAKE IT WITH YOU','Clothing':'YOUR WARDROBE','Watches':'THE FINISHING TOUCH','Jewellery':'A LITTLE DETAIL'}[category] || 'CATALOGUE FIND');
const categoryIcon = category => /Footwear/.test(category) ? 'shoe' : /Mobiles|Computers/.test(category) ? 'headphones' : /Clothing/.test(category) ? 'shirt' : /Home|Kitchen|Furniture/.test(category) ? 'home' : 'bag';
function imageMarkup(p, extra = '') {
  const src = imageURL(p.image_url);
  return `<span class="image-fallback" ${src ? 'hidden' : ''}>${icon(categoryIcon(p.category || ''))}<span>Photo unavailable</span></span>${src ? `<img src="${escapeHTML(src)}" alt="${escapeHTML(p.name)}" loading="lazy" referrerpolicy="no-referrer" ${extra}>` : ''}`;
}
function bindImageFallbacks(root) { $$('img', root).forEach(img => { img.addEventListener('error', () => { img.hidden = true; img.parentElement.classList.add('image-missing'); const fallback = $('.image-fallback', img.parentElement); if (fallback) fallback.hidden = false; }, {once: true}); if (img.complete && !img.naturalWidth) { img.hidden = true; img.parentElement.classList.add('image-missing'); const fallback = $('.image-fallback', img.parentElement); if (fallback) fallback.hidden = false; } }); }
function renderProducts() {
  const list = [...state.products];
  switch ($('#sort-select').value) { case 'price-low': list.sort((a,b) => a.price-b.price); break; case 'price-high': list.sort((a,b) => b.price-a.price); break; case 'rating': list.sort((a,b) => (b.rating ?? -1)-(a.rating ?? -1)); break; }
  $('#product-grid').setAttribute('aria-busy','false');
  $('#product-grid').innerHTML = list.map((p,i) => `<article class="product-card" style="animation-delay:${Math.min(i, 7)*35}ms"><div class="product-visual"><button class="product-image-button" data-detail="${escapeHTML(p.id)}" aria-label="View ${escapeHTML(p.name)}">${imageMarkup(p)}</button><span class="product-kind">${escapeHTML(categoryLabel(p.category))}</span><button class="save-button ${isSaved(p.id) ? 'saved' : ''}" data-id="${escapeHTML(p.id)}" data-name="${escapeHTML(p.name)}" aria-pressed="${isSaved(p.id)}" aria-label="${isSaved(p.id) ? 'Remove' : 'Save'} ${escapeHTML(p.name)}">${icon('heart')}</button></div><div class="product-info"><div class="product-meta"><span class="product-brand">${escapeHTML(p.brand === 'Unknown' ? 'From the catalogue' : p.brand)}</span><span class="product-rating">${p.rating == null ? 'Unrated' : `${icon('star')}${Number(p.rating).toFixed(1)}`}</span></div><button class="product-title" data-detail="${escapeHTML(p.id)}">${escapeHTML(p.name)}</button><div class="product-bottom"><span class="product-price"><small>INR</small>${money(p.price)}</span><button class="detail-link" data-detail="${escapeHTML(p.id)}">Take a closer look</button></div></div></article>`).join('');
  $('#results-count').textContent = `${list.length} catalogue ${list.length === 1 ? 'find' : 'finds'}`;
  $('#empty-state').hidden = list.length !== 0;
  $('#search-status').textContent = `${list.length} ${list.length === 1 ? 'product' : 'products'} found${state.query ? ` for ${state.query}` : ''}.`;
  bindImageFallbacks($('#product-grid')); updateSaveButtons(); renderAIMatchSummary();
}
function skeletons() { $('#product-grid').setAttribute('aria-busy','true'); $('#empty-state').hidden = true; $('#results-count').textContent = 'Finding your matches…'; $('#product-grid').innerHTML = Array.from({length: 8}, () => '<div class="skeleton-card" aria-hidden="true"><div class="skeleton-visual"></div><div class="skeleton-line short"></div><div class="skeleton-line"></div><div class="skeleton-line short"></div></div>').join(''); $('#search-status').textContent = 'Searching the catalogue. This may take a moment on the first search.'; }
function setBusy(busy) { const button = $('.search-submit'); button.disabled = busy; button.innerHTML = busy ? `${icon('spark')}<span>Finding your match…</span>` : `${icon('spark')}<span>Find my match</span>`; }
async function api(path, options = {}) {
  const response = await fetch(path, options);
  let data;
  try { data = await response.json(); } catch { throw new Error('The catalogue didn’t respond as expected. Please try again.'); }
  if (!response.ok) { const message = typeof data.detail === 'string' ? data.detail : Array.isArray(data.detail) ? data.detail.map(d => d.msg).join('. ') : 'Something went wrong. Please try again.'; throw new Error(message); }
  return data;
}
function constraints() { const c = {}; const budget = $('#budget-filter').value; const category = $('#category-filter').value; const rating = $('#rating-filter').value; if (budget) c.max_price = Number(budget); if (category) c.category = category; if (rating) c.min_rating = Number(rating); return c; }
function updateFilterDot() { $('.filter-dot').hidden = Object.keys(constraints()).length === 0; }
function renderConstraints() {
  const c = state.constraints; const chips = [];
  if (c.category) chips.push(c.category);
  if (c.max_price != null) chips.push(`Up to INR ${money(c.max_price)}`);
  if (c.min_price != null) chips.push(`From INR ${money(c.min_price)}`);
  if (c.brand) chips.push(`Brand: ${c.brand}`);
  if (c.min_rating != null) chips.push(`${c.min_rating}+ catalogue rating`);
  const target = $('#active-constraints'); target.hidden = !chips.length;
  target.innerHTML = chips.map(s => `<span class="constraint-chip">${escapeHTML(s)}</span>`).join('') + (chips.length ? '<button class="clear-search">Clear preferences</button>' : '');
}
function chooseTab(category) { $$('.category-tab').forEach(b => { const active = b.dataset.category === category; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active)); }); }
function setHeading(search) { $('#results-eyebrow').textContent = search ? 'MATCHED TO WHAT YOU HAVE IN MIND' : 'THE DISCOVERY EDIT'; $('#results-heading').textContent = search ? 'Let’s find your kind of good.' : 'A few things to catch your eye.'; $('#results-subtitle').textContent = search ? `Catalogue matches for “${state.query}”` : 'A starting point for your next great find.'; }
async function search(query, {scroll = true} = {}) {
  const text = query.trim(); if (text.length < 2) { $('#query').focus(); return; }
  $('#query').value = text;
  if (!$('#search-form').reportValidity()) return false;
  state.controller?.abort(); const controller = new AbortController(); state.controller = controller;
  $('#empty-message').textContent = 'No products match all your preferences. A wider budget or fewer filters could help.'; state.query = text; $('#query').value = text; state.constraints = constraints(); setHeading(true); renderConstraints(); skeletons(); setBusy(true);
  if (scroll) $('#discovery').scrollIntoView({behavior:'smooth', block:'start'});
  try {
    const data = await api('/recommend', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:text,k:8,method:state.semantic ? 'hybrid' : 'tfidf',constraints:state.constraints}),signal:controller.signal});
    if (controller !== state.controller) return;
    state.products = data.products; state.constraints = data.constraints; renderConstraints(); renderProducts(); return true;
  } catch (error) {
    if (error.name === 'AbortError') return;
    state.products = []; renderProducts(); $('#empty-message').textContent = error.message; $('#results-heading').textContent = 'A little pause in the search.'; $('#search-status').textContent = error.message; return false;
  } finally { if (controller === state.controller) { setBusy(false); $('#empty-message').textContent = $('#empty-state').hidden ? 'No products match all your preferences. A wider budget or fewer filters could help.' : $('#empty-message').textContent; } }
}
async function discover({scroll = false} = {}) {
  state.controller?.abort(); const controller = new AbortController(); state.controller = controller;
  state.query = ''; state.constraints = {}; $('#query').value = ''; resetFilters(); chooseTab(''); setHeading(false); renderConstraints(); skeletons(); setBusy(false);
  if (scroll) $('#discovery').scrollIntoView({behavior:'smooth', block:'start'});
  try { const data = await api('/discover', {signal:controller.signal}); if (controller !== state.controller) return; state.products = data.products; renderProducts(); }
  catch (error) { if (error.name === 'AbortError') return; state.products = []; renderProducts(); $('#empty-message').textContent = 'We couldn’t reach the catalogue. Check that the app is running, then try again.'; }
}
function resetFilters() { $('#category-filter').value = ''; $('#budget-filter').value = ''; $('#rating-filter').value = ''; updateFilterDot(); $('#empty-message').textContent = 'No products match all your preferences. A wider budget or fewer filters could help.'; }
function renderShortlist() {
  const target = $('#shortlist-items');
  if (!saved.length) { target.innerHTML = `<div class="empty-state"><span class="empty-icon">${icon('heart')}</span><h3>Room for your next favourite.</h3><p>Tap a heart on any product to keep it here. Your good finds will be waiting.</p><button class="dark-button continue-exploring">Keep exploring</button></div>`; return; }
  target.innerHTML = saved.map(p => `<article class="shortlist-item"><button class="shortlist-image" data-detail="${escapeHTML(p.id)}" aria-label="View ${escapeHTML(p.name)}">${imageMarkup(p)}</button><div class="shortlist-copy"><h3>${escapeHTML(p.name)}</h3><p>INR ${money(p.price)}</p><button data-detail="${escapeHTML(p.id)}">View details</button></div><button class="icon-button remove-saved" data-id="${escapeHTML(p.id)}" aria-label="Remove ${escapeHTML(p.name)} from shortlist">${icon('close')}</button></article>`).join('');
  bindImageFallbacks(target);
}
function openDialog(dialog) { if (!dialog.open) dialog.showModal(); document.body.style.overflow = 'hidden'; }
function closeDialog(dialog) { dialog.close(); if (!$('dialog[open]')) document.body.style.overflow = ''; }
async function showDetails(id) {
  state.detailController?.abort(); const controller = new AbortController(); state.detailController = controller;
  if ($('#shortlist-dialog').open) closeDialog($('#shortlist-dialog'));
  if ($('#assistant-dialog').open) closeDialog($('#assistant-dialog'));
  const dialog = $('#product-dialog'); $('#product-details').innerHTML = '<div class="empty-state"><span class="empty-icon">'+icon('bag')+'</span><h3 id="detail-title">Taking a closer look…</h3><p>Fetching the original catalogue details.</p></div>'; openDialog(dialog);
  try {
    const p = await api(`/products/${encodeURIComponent(id)}`, {signal:controller.signal}); if (controller !== state.detailController) return; state.detailId = p.id;
    const retailerURL = safeURL(p.url); const c = state.constraints; const reasons = [];
    if (state.products.some(item => item.id === p.id) && state.query) { if (c.max_price != null && p.price <= c.max_price) reasons.push(`Within your INR ${money(c.max_price)} budget`); if (c.category === p.category) reasons.push(`In your ${p.category} category`); if (c.min_rating != null && p.rating >= c.min_rating) reasons.push('Meets your rating preference'); }
    $('#product-details').innerHTML = `<div class="detail-layout"><div class="detail-visual">${imageMarkup(p)}</div><div class="detail-copy"><span class="eyebrow">${escapeHTML(p.brand === 'Unknown' ? 'A CATALOGUE FIND' : p.brand)}</span><h2 id="detail-title">${escapeHTML(p.name)}</h2><span class="product-rating">${p.rating == null ? 'No catalogue rating available' : `${icon('star')} ${Number(p.rating).toFixed(1)} / 5 · catalogue rating`}</span><div class="detail-price"><small>INR</small>${money(p.price)}</div><div class="detail-facts"><span class="detail-fact">${escapeHTML(p.category)}</span><span class="detail-fact">Stock unknown</span></div>${reasons.length ? `<p class="detail-source-note">${reasons.map(r => `${icon('check')} ${escapeHTML(r)}`).join('<br>')}</p>` : ''}<p class="detail-description">${escapeHTML(p.description || 'The original listing has no description. Confirm product specifications with the retailer.')}</p><div class="detail-buttons">${retailerURL ? `<a class="dark-button" href="${escapeHTML(retailerURL)}" target="_blank" rel="noopener noreferrer">Explore the retailer ${icon('external')}</a>` : ''}<button class="detail-save" data-id="${escapeHTML(p.id)}" aria-pressed="${isSaved(p.id)}">${icon('heart')} ${isSaved(p.id) ? 'Saved to shortlist' : 'Save for later'}</button></div><p class="detail-source-note">A historical listing, not a live offer. Price, availability and retailer links may have changed. Confirm details before purchasing.</p></div></div>`;
    $('.detail-save',dialog).addEventListener('click', () => toggleSave(p)); bindImageFallbacks(dialog);
  } catch (error) { if (error.name === 'AbortError') return; $('#product-details').innerHTML = `<div class="empty-state"><h3 id="detail-title">We couldn’t open that find.</h3><p>${escapeHTML(error.message)}</p></div>`; }
}
$('#search-form').addEventListener('submit', event => {event.preventDefault(); chooseTab($('#category-filter').value); search($('#query').value);});
$('#filter-toggle').addEventListener('click', () => { const panel = $('#filters-panel'); panel.hidden = !panel.hidden; $('#filter-toggle').setAttribute('aria-expanded', String(!panel.hidden)); });
$('#reset-filters').addEventListener('click', () => { resetFilters(); chooseTab(''); if (state.query) search(state.query, {scroll:false}); });
$$('#filters-panel input, #filters-panel select').forEach(el => el.addEventListener('change', updateFilterDot));
$('#sort-select').addEventListener('change', renderProducts);
$$('.prompt-chip, .collection-card').forEach(b => b.addEventListener('click', () => {resetFilters(); chooseTab(''); $('#query').value = b.dataset.query; search(b.dataset.query);}));
$$('.category-tab').forEach(b => b.addEventListener('click', () => {resetFilters(); if (!b.dataset.query) {discover(); return;} $('#category-filter').value=b.dataset.category; chooseTab(b.dataset.category); updateFilterDot(); $('#query').value=b.dataset.query; search(b.dataset.query,{scroll:false});}));
$('#product-grid').addEventListener('click', event => { const save = event.target.closest('.save-button'); if (save) { const p = state.products.find(p => p.id === save.dataset.id); if (p) toggleSave(p); return;} const detail = event.target.closest('[data-detail]'); if (detail) showDetails(detail.dataset.detail); });
$('#shortlist-items').addEventListener('click', event => { const remove = event.target.closest('.remove-saved'); if (remove) { const p = saved.find(p => p.id === remove.dataset.id); if (p) toggleSave(p); return;} const detail=event.target.closest('[data-detail]'); if(detail) showDetails(detail.dataset.detail); if(event.target.closest('.continue-exploring')) closeDialog($('#shortlist-dialog')); });
$('#active-constraints').addEventListener('click', event => { if (event.target.closest('.clear-search')) {resetFilters();chooseTab('');search(state.query);} });
$('#shortlist-button').addEventListener('click', () => {renderShortlist();openDialog($('#shortlist-dialog'));});
$('#start-search').addEventListener('click', () => {$('#query').scrollIntoView({behavior:'smooth',block:'center'});$('#query').focus({preventScroll:true});});
$('#discover-nav').addEventListener('click', () => discover({scroll:true}));
$('#collections-nav').addEventListener('click', () => $('#collections').scrollIntoView({behavior:'smooth'}));
$('#insights-nav').addEventListener('click', () => $('#insights').scrollIntoView({behavior:'smooth'}));
$('#data-info-button').addEventListener('click', () => openDialog($('#info-dialog')));
$('.info-done').addEventListener('click', () => closeDialog($('#info-dialog')));
$('#empty-reset').addEventListener('click', () => discover());
$$('dialog').forEach(dialog => { $('.dialog-close',dialog).addEventListener('click', () => closeDialog(dialog)); dialog.addEventListener('click', event => {if (event.target === dialog) {const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left || event.clientX>rect.right || event.clientY<rect.top || event.clientY>rect.bottom) closeDialog(dialog);}}); dialog.addEventListener('close', () => {if (!$('dialog[open]')) document.body.style.overflow=''; if(dialog.id==='product-dialog') state.detailController?.abort();}); });
document.addEventListener('keydown', event => {if(event.key==='/' && !['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName) && !$('dialog[open]')){event.preventDefault();$('#query').focus();}});
async function initialize() {
  updateSaveButtons(); renderShortlist();
  try { const data = await api('/catalogue'); state.semantic = data.semantic_available; data.categories.forEach(c => { const option=document.createElement('option'); option.value=c.name; option.textContent=`${c.name} (${c.count.toLocaleString()})`; $('#category-filter').append(option); }); }
  catch { /* Discovery displays the actionable connection error. */ }
  await Promise.all([discover(), loadInsights()]);
}

function renderAIMatchSummary() {
  const el=$('#ai-match-summary'); el.hidden=!state.query || !state.products.length;
  if(el.hidden)return;
  const c=state.constraints;
  const description=[`${state.products.length} catalogue matches`,c.max_price!=null?`all within INR ${money(c.max_price)}`:'ranked for your request',c.category?`in ${c.category}`:''].filter(Boolean).join(' · ');
  el.innerHTML=`<span class="match-ai-icon">${icon('spark')}</span><div><strong>Your request, thoughtfully matched.</strong><p>${escapeHTML(description)}. ${state.semantic?'Semantic + keyword retrieval':'Keyword retrieval'}; product facts come from the catalogue.</p></div><button class="match-ask">Refine with AI</button>`;
  $('.match-ask',el).addEventListener('click',openAssistant);
}
function openAssistant() { openDialog($('#assistant-dialog')); $('#chat-input').focus(); }
$$('#assistant-nav, #ask-ai-button, #ai-launcher').forEach(button=>button.addEventListener('click',openAssistant));
let chatBusy=false, lastChatIntent='';
function appendChat(role,text,products=[]) {
  const bubble=document.createElement('div');bubble.className=`chat-bubble ${role==='user'?'user-bubble':'assistant-bubble'}`;
  bubble.innerHTML=`<span class="chat-author">${role==='user'?'YOU':'RETAILASSIST'}</span><p>${escapeHTML(text)}</p>`;
  if(products.length){const list=document.createElement('div');list.className='chat-picks';list.innerHTML=products.slice(0,3).map(p=>`<button data-detail="${escapeHTML(p.id)}"><span>${escapeHTML(p.name)}</span><strong>INR ${money(p.price)}</strong></button>`).join('');bubble.append(list);const view=document.createElement('button');view.className='chat-view-matches';view.textContent='Explore all matches';view.addEventListener('click',()=>{closeDialog($('#assistant-dialog'));$('#discovery').scrollIntoView({behavior:'smooth'});});bubble.append(view);}
  $('#chat-messages').append(bubble);bubble.scrollIntoView({behavior:'smooth',block:'nearest'});return bubble;
}
async function askAssistant(text) {
  const question=text.trim();if(chatBusy || question.length<2)return;
  chatBusy=true;$('#chat-send').disabled=true;$('#chat-input').value='';appendChat('user',question);
  const thinking=appendChat('assistant','Finding possibilities in the catalogue…');thinking.classList.add('chat-thinking');
  let query=question;
  if(lastChatIntent && /^(?:please\s+)?(?:only\s+)?(?:under|below|up to|at most|budget|show me (?:ones|options|products) (?:under|below))\b/i.test(question))query=`${lastChatIntent}. ${question}`;
  lastChatIntent=query.replace(/(?:under|below|up to|at most|budget(?: of)?)\s*(?:inr|rs\.?|₹)?\s*[\d,]+(?:\.\d+)?\s*(?:k\b)?/gi,'').trim();
  const budget=question.match(/(?:under|below|up to|at most|budget(?: of)?)\s*(?:inr|rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?/i);
  if(budget)$('#budget-filter').value=Number(budget[1].replaceAll(',',''))*(budget[2]?1000:1);
  updateFilterDot();
  try{
    const completed=await search(query,{scroll:false});thinking.remove();
    if(!completed){appendChat('assistant',$('#search-status').textContent || 'Please check your filters and try again.');return;}
    if(state.products.length){const prices=state.products.map(p=>p.price);let reply=`I found ${state.products.length} catalogue products for you, priced from INR ${money(Math.min(...prices))} to INR ${money(Math.max(...prices))}.`;
      if(state.constraints.max_price!=null)reply+=` Every result is within your INR ${money(state.constraints.max_price)} budget.`;
      if(state.constraints.category)reply+=` I kept your ${state.constraints.category} category filter.`;
      reply+=(state.semantic?' I matched the meaning of your request with catalogue text.':' I searched the catalogue using your keywords.')+' Current stock is unknown, so confirm details with the retailer.';
      appendChat('assistant',reply,state.products);
    }else appendChat('assistant',$('#empty-message').textContent+' You can change the filters or give me a different budget.');
  }finally{chatBusy=false;$('#chat-send').disabled=false;$('#chat-input').focus();}
}
$('#chat-form').addEventListener('submit',event=>{event.preventDefault();if($('#chat-form').reportValidity())askAssistant($('#chat-input').value);});
$('#chat-input').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();$('#chat-form').requestSubmit();}});
$$('[data-chat-query]').forEach(button=>button.addEventListener('click',()=>askAssistant(button.dataset.chatQuery)));
$('#chat-messages').addEventListener('click',event=>{const button=event.target.closest('[data-detail]');if(button)showDetails(button.dataset.detail);});
let insightsData=null, selectedMetric='ndcg_at_5';
const metricDefinitions={ndcg_at_5:{label:'NDCG@5',explain:'Rewards relevant products appearing near the top. Scores are normalized from 0 to 1.'},precision_at_5:{label:'Precision@5',explain:'The share of the first five results matching the rule-based relevance labels.'},recall_at_5:{label:'Recall@5',explain:'The share of all labelled relevant catalogue products retrieved in the first five.'},mrr_at_5:{label:'MRR@5',explain:'How early the first labelled relevant result appears, up to position five.'}};
function modelBars(){
 const test=insightsData.evaluation.filter(r=>r.split==='test');const order=['hybrid','semantic','tfidf','lsa'];const names={hybrid:'Hybrid',semantic:'Semantic · MiniLM',tfidf:'Keyword · TF-IDF',lsa:'Latent semantic · SVD'};
 return order.filter(name=>test.some(r=>r.method===name)).map(name=>{const row=test.find(r=>r.method===name);const value=Number(row[selectedMetric]);return `<div class="model-bar-row"><div><span>${names[name]}</span><strong>${value.toFixed(3)}</strong></div><div class="bar-track"><span class="${name==='hybrid'?'bar-primary':''}" style="width:${Math.max(0,Math.min(100,value*100))}%"></span></div></div>`;}).join('');
}
function renderInsights(){
 const data=insightsData,c=data.catalogue;const total=c.total_products;const percent=n=>total?Math.round(n/total*100):0;const test=data.evaluation.filter(r=>r.split==='test');const hybrid=test.find(r=>r.method==='hybrid');const knownBrand=total-c.unknown_brands;const catMax=Math.max(...c.top_categories.map(v=>v.count),1);const priceMax=Math.max(...c.price_distribution.map(v=>v.count),1);
 $('#insights-content').innerHTML=`<div class="insight-stats"><article><span>${icon('bag')}Catalogue products</span><strong>${total.toLocaleString()}</strong><small>Cleaned, unique product IDs</small></article><article><span>${icon('grid')}Distinct known brands</span><strong>${c.brands.toLocaleString()}</strong><small>${percent(knownBrand)}% of products have a known brand</small></article><article><span>${icon('spark')}Hybrid precision@5</span><strong>${hybrid?(Number(hybrid.precision_at_5)*100).toFixed(1)+'%':'Not evaluated'}</strong><small>${hybrid?'On '+hybrid.queries+' silver-labelled test queries':'Run the evaluation pipeline'}</small></article><article><span>${icon('sliders')}Median listed price</span><strong><em>INR</em> ${money(c.median_price)}</strong><small>Historical prices, not live offers</small></article></div><div class="insight-chart-grid"><article class="insight-panel model-panel"><div class="panel-title"><div><span class="eyebrow">THE MODEL COMPARISON</span><h3>Does meaning make a difference?</h3></div><span class="offline-tag">Offline evaluation</span></div><div class="metric-tabs" role="group" aria-label="Choose an evaluation metric">${Object.entries(metricDefinitions).map(([key,v])=>`<button data-metric="${key}" class="${key===selectedMetric?'active':''}" aria-pressed="${key===selectedMetric}">${v.label}</button>`).join('')}</div><div id="model-bars">${test.length?modelBars():'<p>Run the evaluation pipeline to populate this comparison.</p>'}</div><p class="metric-explanation" id="metric-explanation">${metricDefinitions[selectedMetric].explain}</p><p class="insight-caveat">24 test queries · rule-based silver labels · binary relevance. These results do not measure real shopper satisfaction.</p></article><article class="insight-panel quality-panel"><span class="eyebrow">A CLEARER PICTURE OF THE DATA</span><h3>Good recommendations<br>start with honest data.</h3><div class="quality-line"><span>Known brands</span><strong>${percent(knownBrand)}%</strong></div><div class="bar-track"><span style="width:${percent(knownBrand)}%"></span></div><div class="quality-line"><span>Products with numeric ratings</span><strong>${percent(c.rated_products)}%</strong></div><div class="bar-track"><span style="width:${percent(c.rated_products)}%"></span></div><div class="quality-notice">${icon('info')}<p><strong>Stock is unknown.</strong> We never turn a missing value into an availability claim.</p></div><span class="model-signature">${icon('spark')} ${escapeHTML(data.model.name)}<small>Hybrid: 75% semantic + 25% keyword similarity</small></span></article></div><div class="insight-chart-grid catalogue-chart-grid"><article class="insight-panel"><span class="eyebrow">WHAT’S IN THE CATALOGUE</span><h3>Room for every kind of find.</h3><div class="category-bars">${c.top_categories.map(item=>`<div><span>${escapeHTML(item.name)}</span><div class="bar-track"><span style="width:${item.count/catMax*100}%"></span></div><strong>${item.count.toLocaleString()}</strong></div>`).join('')}</div></article><article class="insight-panel"><span class="eyebrow">FIND YOUR PRICE RANGE</span><h3>A budget for every possibility.</h3><div class="price-histogram">${c.price_distribution.map(item=>`<div class="histogram-column"><span class="histogram-count">${item.count.toLocaleString()}</span><div><span style="height:${Math.max(item.count?2:0,item.count/priceMax*100)}%"></span></div><span class="histogram-label">${escapeHTML(item.label)}</span></div>`).join('')}</div><p class="insight-caveat">Listed prices in INR. Distribution describes catalogue supply, not sales or demand.</p></article></div><p class="insights-disclosure">${icon('shield')}${escapeHTML(data.evaluation_note)}</p>`;
 $$('[data-metric]').forEach(button=>button.addEventListener('click',()=>{selectedMetric=button.dataset.metric;$$('[data-metric]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});$('#model-bars').innerHTML=modelBars();$('#metric-explanation').textContent=metricDefinitions[selectedMetric].explain;}));
}
async function loadInsights(){try{insightsData=await api('/insights');renderInsights();}catch{$('#insights-content').innerHTML='<p class="insights-loading">The insights couldn’t load. Refresh once the catalogue service is available.</p>';}}
initialize();
