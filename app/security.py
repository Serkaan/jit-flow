from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .models import User, Role, get_db

oauth2=OAuth2PasswordBearer(tokenUrl='/api/auth/token')
def token_for(user: User):
    return jwt.encode({'sub':user.username,'role':user.role.value,'exp':datetime.now(timezone.utc)+timedelta(minutes=60)},settings.JWT_SECRET,algorithm='HS256')
def current_user(token=Depends(oauth2), db:Session=Depends(get_db)):
    try: name=jwt.decode(token,settings.JWT_SECRET,algorithms=['HS256'])['sub']
    except Exception: raise HTTPException(401,'Geçersiz veya süresi dolmuş token')
    u=db.query(User).filter_by(username=name,active=True).first()
    if not u: raise HTTPException(401,'Kullanıcı bulunamadı')
    return u
def roles(*allowed):
    def dep(u=Depends(current_user)):
        if u.role not in allowed: raise HTTPException(403,'Bu işlem için rolünüz yetersiz')
        return u
    return dep
