import ssl
from ldap3 import Server, Connection, Tls, SUBTREE, MODIFY_ADD, MODIFY_DELETE
from ..config import settings
class ADError(Exception): pass
class FakeAD:
    users={'ahmet','mehmet','ayse','fatma','requester','manager','admin'}
    groups={'domain admins','backup operators','server operators','dnsadmins','helpdesk readers','sql operators','file share admins'}
    members={}
    def validate(self,user,group):
        if user.lower() not in self.users: raise ADError(f'Kullanıcı bulunamadı: {user}')
        if group.lower() not in self.groups: raise ADError(f'Grup bulunamadı: {group}')
    def add(self,user,group): self.validate(user,group); self.members.setdefault(group.lower(),set()).add(user.lower()); return True
    def remove(self,user,group): self.validate(user,group); self.members.setdefault(group.lower(),set()).discard(user.lower()); return True
    def health(self): return {'ok':True,'mode':'fake'}
class LDAPAD:
    def conn(self):
        tls=Tls(validate=ssl.CERT_REQUIRED if settings.AD_VALIDATE_CERT else ssl.CERT_NONE,ca_certs_file=settings.AD_CA_CERT_FILE or None)
        try: return Connection(Server(settings.AD_SERVER,port=settings.AD_PORT,use_ssl=settings.AD_USE_SSL,tls=tls,connect_timeout=8),user=settings.AD_BIND_DN,password=settings.AD_BIND_PASSWORD,auto_bind=True,raise_exceptions=True)
        except Exception as e: raise ADError(f'AD bind başarısız: {e}')
    @staticmethod
    def esc(s): return ''.join({'\\':'\\5c','*':'\\2a','(':'\\28',')':'\\29','\0':'\\00'}.get(c,c) for c in s)
    def dns(self,user,group):
        with self.conn() as c:
            c.search(settings.AD_BASE_DN,f'(&(objectClass=user)(sAMAccountName={self.esc(user)}))',SUBTREE,attributes=['distinguishedName','userAccountControl'])
            if len(c.entries)!=1: raise ADError(f'Kullanıcı bulunamadı veya tekil değil: {user}')
            if int(c.entries[0].userAccountControl.value or 0)&2: raise ADError('Kullanıcı hesabı devre dışı')
            udn=str(c.entries[0].distinguishedName.value)
            c.search(settings.AD_BASE_DN,f'(&(objectClass=group)(|(cn={self.esc(group)})(sAMAccountName={self.esc(group)})))',SUBTREE,attributes=['distinguishedName','member'])
            if len(c.entries)!=1: raise ADError(f'Grup bulunamadı veya tekil değil: {group}')
            return udn,str(c.entries[0].distinguishedName.value),[str(x) for x in c.entries[0].member.values]
    def add(self,user,group):
        u,g,m=self.dns(user,group)
        if u in m:return True
        with self.conn() as c:
            if not c.modify(g,{'member':[(MODIFY_ADD,[u])]}): raise ADError(str(c.result))
        return True
    def remove(self,user,group):
        u,g,m=self.dns(user,group)
        if u not in m:return True
        with self.conn() as c:
            if not c.modify(g,{'member':[(MODIFY_DELETE,[u])]}): raise ADError(str(c.result))
        return True
    def health(self):
        try:
            with self.conn() as c:return {'ok':c.bound,'mode':'ldap','server':settings.AD_SERVER}
        except Exception as e:return {'ok':False,'mode':'ldap','error':str(e)}
ad = FakeAD() if settings.AD_MODE.lower()=='fake' else LDAPAD()
