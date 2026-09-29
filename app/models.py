from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Integer, DateTime, Text, Boolean, ForeignKey, Enum as SAEnum, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings

def utcnow(): return datetime.now(timezone.utc)
class Base(DeclarativeBase): pass
class Role(str, Enum):
    ADMIN='Admin'; MANAGER='Manager'; REQUESTER='Requester'
class Status(str, Enum):
    PENDING='Pending'; ACTIVE='Active'; REJECTED='Rejected'; REVOKED='Revoked'; EXPIRED='Expired'; FAILED='Failed'
class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    username: Mapped[str]=mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str]=mapped_column(String(200), default='')
    role: Mapped[Role]=mapped_column(SAEnum(Role), default=Role.REQUESTER)
    active: Mapped[bool]=mapped_column(Boolean, default=True)
class AccessRequest(Base):
    __tablename__='requests'
    id: Mapped[int]=mapped_column(primary_key=True)
    requester_id: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    target_user: Mapped[str]=mapped_column(String(120), index=True)
    target_group: Mapped[str]=mapped_column(String(200), index=True)
    justification: Mapped[str]=mapped_column(Text)
    raw_text: Mapped[str]=mapped_column(Text)
    duration_minutes: Mapped[int]=mapped_column(Integer)
    status: Mapped[Status]=mapped_column(SAEnum(Status), default=Status.PENDING, index=True)
    risk_score: Mapped[int]=mapped_column(Integer, default=50)
    risk_level: Mapped[str]=mapped_column(String(20), default='MEDIUM')
    risk_summary: Mapped[str]=mapped_column(Text, default='')
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow)
    approved_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True, index=True)
    revoked_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True), nullable=True)
    approver: Mapped[str|None]=mapped_column(String(120), nullable=True)
    revoke_attempts: Mapped[int]=mapped_column(Integer, default=0)
    last_error: Mapped[str|None]=mapped_column(Text, nullable=True)
class AuditLog(Base):
    __tablename__='audit_logs'
    id: Mapped[int]=mapped_column(primary_key=True)
    ts: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    action: Mapped[str]=mapped_column(String(80), index=True)
    actor: Mapped[str]=mapped_column(String(120), default='system')
    request_id: Mapped[int|None]=mapped_column(Integer, nullable=True, index=True)
    success: Mapped[bool]=mapped_column(Boolean, default=True)
    ip: Mapped[str|None]=mapped_column(String(64), nullable=True)
    detail: Mapped[str]=mapped_column(Text, default='')

engine=create_engine(settings.DATABASE_URL, connect_args={'check_same_thread':False} if settings.DATABASE_URL.startswith('sqlite') else {}, pool_pre_ping=True)
@event.listens_for(engine,'connect')
def pragmas(conn,_):
    if settings.DATABASE_URL.startswith('sqlite'):
        c=conn.cursor(); c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA foreign_keys=ON'); c.close()
SessionLocal=sessionmaker(bind=engine, expire_on_commit=False)
def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.query(User).count():
            db.add_all([User(username='admin',display_name='Admin',role=Role.ADMIN),User(username='manager',display_name='Manager',role=Role.MANAGER),User(username='requester',display_name='Requester',role=Role.REQUESTER)]); db.commit()
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
