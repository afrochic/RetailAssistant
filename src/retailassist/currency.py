"""Dated reference conversion, never represented as Kenyan inventory."""
import re
from decimal import Decimal, ROUND_HALF_UP
FX = {'base':'INR','quote':'KES','rate':1.37,'valid_from':'2026-11-16','valid_to':'2026-11-22','source':'https://www.kra.go.ke/images/foreignexchange/EXCHANGE-RATE-RUNNING-FROM-16th-November-2026-to-22nd-November-2026.pdf','type':'KRA weekly reference rate; estimated conversion, not a current Kenyan retail price'}
def resolve_currency(query='',requested=None):
    if re.search(r'\b(?:usd|dollars|eur|euros)\b',query,re.I): raise ValueError('Supported currencies are INR and estimated KES.')
    kes=bool(re.search(r'\b(?:kes|ksh|kshs)\b',query,re.I));inr=bool(re.search(r'\b(?:inr|rs)\b|₹',query,re.I))
    if kes and inr:raise ValueError('Use one currency per request: INR or KES.')
    detected='KES' if kes else 'INR' if inr else None
    if requested and requested not in ['INR','KES']:raise ValueError('Supported currencies are INR and KES.')
    if detected and requested and detected!=requested:raise ValueError('Query currency conflicts with the selected currency.')
    return detected or requested or 'INR'
def convert_price(value,currency):
    return float((Decimal(str(value))*(Decimal(str(FX['rate'])) if currency=='KES' else Decimal('1'))).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def present_product(product,currency):
    source=product.get('source_price',product['price']);p={**product,'source_price':source,'source_currency':'INR','price':convert_price(source,currency),'currency':currency,'price_is_estimate':currency=='KES'}
    if currency=='KES':p['conversion']=FX
    return p
