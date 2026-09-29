from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from .config import settings
from .models import init_db,get_db,User,Role,AccessRequest,Status,AuditLog
from .security import token_for,current_user,roles
from .services.ad import ad
from .services.ai import analyze,FORBIDDEN,PROTECTED
from .services.ops import audit,revoke_one,scan_expired
scheduler=BackgroundScheduler()
@asynccontextmanager
async def life(app):
    init_db();scheduler.add_job(scan_expired,'interval',seconds=settings.REVOKE_SCAN_INTERVAL_SECONDS,id='revoke',replace_existing=True,max_instances=1);scheduler.start();yield;scheduler.shutdown(wait=False)
app=FastAPI(title='JIT-Flow',version='2.0',lifespan=life)
class ReqIn(BaseModel):
    text:str=Field(min_length=10,max_length=4000);target_samaccountname:str;target_group:str;duration_minutes:int=Field(ge=5,le=1440);justification:str|None=None
class ApproveIn(BaseModel): acknowledge_risk:bool=False;note:str='';duration_minutes:int|None=None
class RejectIn(BaseModel): reason:str=Field(min_length=3)
def out(r):return {k:getattr(r,k) for k in ['id','target_user','target_group','justification','duration_minutes','status','risk_score','risk_level','risk_summary','created_at','approved_at','expires_at','revoked_at','approver','revoke_attempts','last_error']}
@app.post('/api/auth/token')
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.query(User).filter_by(username=form.username,active=True).first()
    if not u:raise HTTPException(401,'Geçersiz kullanıcı')
    return {'access_token':token_for(u),'token_type':'bearer','role':u.role.value}
@app.get('/api/me')
def me(u=Depends(current_user)):return {'username':u.username,'display_name':u.display_name,'role':u.role.value}
@app.post('/api/request',status_code=201)
async def create(p:ReqIn,request:Request,db:Session=Depends(get_db),u=Depends(current_user)):
    if p.target_group.lower() in FORBIDDEN:raise HTTPException(403,'Bu grup JIT kapsamı dışındadır; break-glass süreci kullanın')
    try:ad.validate(p.target_samaccountname,p.target_group) if hasattr(ad,'validate') else ad.dns(p.target_samaccountname,p.target_group)
    except Exception as e:raise HTTPException(400,f'AD doğrulama hatası: {e}')
    dur=min(p.duration_minutes,settings.MAX_PROTECTED_DURATION_MINUTES if any(x in p.target_group.lower() for x in PROTECTED) else settings.MAX_DURATION_MINUTES)
    j=p.justification or p.text;risk=await analyze(p.target_group,dur,j,p.text)
    r=AccessRequest(requester_id=u.id,target_user=p.target_samaccountname,target_group=p.target_group,justification=j,raw_text=p.text,duration_minutes=dur,status=Status.PENDING,risk_score=risk['score'],risk_level=risk['level'],risk_summary=risk['summary']);db.add(r);db.commit();db.refresh(r);audit(db,'REQUEST_CREATED',u.username,r.id,True,{'risk':risk},request.client.host if request.client else None);return {'request':out(r),'risk_factors':risk['factors'],'disclaimer':'AI yalnızca tavsiye verir; karar yöneticidedir.'}
@app.get('/api/requests')
def requests(status:str|None=None,db:Session=Depends(get_db),u=Depends(current_user)):
    q=db.query(AccessRequest)
    if u.role==Role.REQUESTER:q=q.filter_by(requester_id=u.id)
    if status:q=q.filter(AccessRequest.status==Status(status))
    return [out(x) for x in q.order_by(AccessRequest.id.desc()).all()]
@app.get('/api/requests/{rid}')
def get_request(rid:int,db:Session=Depends(get_db),u=Depends(current_user)):
    r=db.get(AccessRequest,rid)
    if not r:raise HTTPException(404,'Talep bulunamadı')
    if u.role==Role.REQUESTER and r.requester_id!=u.id:raise HTTPException(403,'Yetkisiz')
    return out(r)
@app.post('/api/approve/{rid}')
def approve(rid:int,p:ApproveIn,db:Session=Depends(get_db),u=Depends(roles(Role.ADMIN,Role.MANAGER))):
    r=db.get(AccessRequest,rid)
    if not r:raise HTTPException(404,'Talep bulunamadı')
    if r.status!=Status.PENDING:raise HTTPException(409,'Talep Pending değil')
    if r.requester_id==u.id:raise HTTPException(403,'Kendi talebinizi onaylayamazsınız')
    if r.risk_score>=60 and not p.acknowledge_risk:raise HTTPException(428,'Yüksek risk açıkça kabul edilmelidir')
    try:ad.add(r.target_user,r.target_group)
    except Exception as e:audit(db,'AD_GRANT_FAILED',u.username,r.id,False,str(e));raise HTTPException(502,f'AD işlem hatası: {e}')
    now=datetime.now(timezone.utc);dur=min(p.duration_minutes or r.duration_minutes,r.duration_minutes);r.status=Status.ACTIVE;r.approver=u.username;r.approved_at=now;r.expires_at=now+timedelta(minutes=dur);db.commit();audit(db,'APPROVED',u.username,r.id,True,{'expires_at':r.expires_at});return out(r)
@app.post('/api/reject/{rid}')
def reject(rid:int,p:RejectIn,db:Session=Depends(get_db),u=Depends(roles(Role.ADMIN,Role.MANAGER))):
    r=db.get(AccessRequest,rid)
    if not r or r.status!=Status.PENDING:raise HTTPException(409,'Talep reddedilemez')
    r.status=Status.REJECTED;r.approver=u.username;db.commit();audit(db,'REJECTED',u.username,r.id,True,p.reason);return out(r)
@app.post('/api/revoke/{rid}')
def revoke(rid:int,u=Depends(roles(Role.ADMIN,Role.MANAGER))):
    if not revoke_one(rid,u.username,True):raise HTTPException(502,'Revoke başarısız')
    return {'ok':True,'request_id':rid}
@app.get('/api/audit')
def logs(limit:int=500,db:Session=Depends(get_db),u=Depends(roles(Role.ADMIN,Role.MANAGER))):
    return [{'id':x.id,'ts':x.ts,'action':x.action,'actor':x.actor,'request_id':x.request_id,'success':x.success,'detail':x.detail} for x in db.query(AuditLog).order_by(AuditLog.id.desc()).limit(min(limit,1000)).all()]
@app.get('/health')
def health():return {'status':'ok','ad':ad.health(),'environment':settings.APP_ENV}
