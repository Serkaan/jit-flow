from datetime import datetime, timezone
import json, httpx
from ..config import settings
from ..models import SessionLocal, AccessRequest, AuditLog, Status
from .ad import ad

def audit(db,action,actor='system',rid=None,success=True,detail='',ip=None):
    db.add(AuditLog(action=action,actor=actor,request_id=rid,success=success,detail=json.dumps(detail,ensure_ascii=False,default=str) if isinstance(detail,(dict,list)) else str(detail),ip=ip)); db.commit()
def alert(title,message):
    if settings.ALERT_WEBHOOK_URL:
        try:httpx.post(settings.ALERT_WEBHOOK_URL,json={'text':f'{title}\n{message}'},timeout=8)
        except Exception:pass
def revoke_one(rid,actor='scheduler',manual=False):
    with SessionLocal() as db:
        r=db.get(AccessRequest,rid)
        if not r:return False
        if r.status!=Status.ACTIVE:return True
        try: ad.remove(r.target_user,r.target_group)
        except Exception as e:
            r.revoke_attempts+=1;r.last_error=str(e);audit(db,'AD_REVOKE_FAILED',actor,r.id,False,str(e))
            if r.revoke_attempts>=settings.REVOKE_MAX_RETRIES:r.status=Status.FAILED;audit(db,'REVOKE_CRITICAL',actor,r.id,False,'Manuel müdahale gerekli');alert('JIT-Flow kritik revoke hatası',f'Talep {r.id}: {e}')
            db.commit();return False
        r.status=Status.REVOKED if manual else Status.EXPIRED;r.revoked_at=datetime.now(timezone.utc);r.last_error=None;db.commit();audit(db,'AD_REVOKE_SUCCESS',actor,r.id,True)
        return True
def scan_expired():
    now=datetime.now(timezone.utc)
    with SessionLocal() as db: ids=[x.id for x in db.query(AccessRequest).filter(AccessRequest.status==Status.ACTIVE,AccessRequest.expires_at<=now).all()]
    for rid in ids: revoke_one(rid)
