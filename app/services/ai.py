import re, httpx
from ..config import settings
PROTECTED=['domain admins','backup operators','server operators','dnsadmins','administrators']
FORBIDDEN=['enterprise admins','schema admins']
def level(s): return 'CRITICAL' if s>=85 else 'HIGH' if s>=60 else 'MEDIUM' if s>=30 else 'LOW'
def assess(group,duration,justification,raw):
    g=group.lower(); score=10; factors=[]
    if g in FORBIDDEN: score+=75; factors.append('JIT kapsamı dışı kritik grup')
    elif any(x in g for x in PROTECTED): score+=50; factors.append('Yüksek ayrıcalıklı grup')
    if duration>120: score+=15; factors.append('Uzun süre')
    if len(justification.strip())<15: score+=15; factors.append('Gerekçe yetersiz')
    if re.search(r'ignore previous|system prompt|otomatik onay|riski düşük|riski dusuk',raw,re.I): score+=25; factors.append('Prompt injection şüphesi')
    score=min(score,100)
    return {'score':score,'level':level(score),'factors':factors,'summary':'; '.join(factors) or 'Belirgin ek risk faktörü bulunmadı'}
async def analyze(group,duration,justification,raw):
    base=assess(group,duration,justification,raw)
    if not settings.LLM_ENABLED or not settings.OPENAI_API_KEY:return base
    prompt=f'Yalnızca JSON döndür: risk_score, risk_summary. AI karar veremez. Grup={group}; süre={duration}; gerekçe={justification}; talep={raw}'
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r=await c.post(settings.OPENAI_BASE_URL.rstrip('/')+'/chat/completions',headers={'Authorization':'Bearer '+settings.OPENAI_API_KEY},json={'model':settings.LLM_MODEL,'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'PAM risk analistisin. Onay veya red kararı verme.'},{'role':'user','content':prompt}]}); r.raise_for_status(); data=r.json()['choices'][0]['message']['content']
        import json; obj=json.loads(data); base['score']=max(base['score'],int(obj.get('risk_score',50))); base['level']=level(base['score']); base['summary']=obj.get('risk_summary',base['summary'])
    except Exception: base['score']=max(base['score'],50); base['level']=level(base['score']); base['summary']+='; LLM erişilemedi, manuel inceleme zorunlu'
    return base
