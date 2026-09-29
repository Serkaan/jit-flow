# JIT-Flow v2.0

Kullanıcı arayüzü, yönetici onay merkezi, audit ekranı, FastAPI backend, LDAP/LDAPS, AI risk analizi ve otomatik revoke içeren çalışır ürün adayı.

## Windows 11 hızlı başlangıç

PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install_windows.ps1
.\.venv\Scripts\python.exe run_all.py
```

Tarayıcı otomatik açılmazsa:
- Kullanıcı arayüzü: http://127.0.0.1:8501
- API dokümanı: http://127.0.0.1:8080/docs

Demo kullanıcıları: `requester`, `manager`, `admin`. Demo parolası herhangi bir değer olabilir. Bu yalnızca geliştirme içindir.

## Kullanım
1. `requester` ile giriş yapıp talep oluşturun.
2. Çıkış yapıp `manager` ile giriş yapın.
3. Onay Merkezi'nden talebi onaylayın veya reddedin.
4. Audit ekranında işlem izini görün.
5. Süre dolunca scheduler otomatik revoke eder.

## AD modları
- `AD_MODE=fake`: localhost demosu.
- `AD_MODE=ldap`: gerçek LDAPS. `.env` içinde DC, bind DN, parola, Base DN ve CA sertifikasını doldurun.

## Sürekli çalıştırma
Windows Server'da `scripts/install_service.ps1` NSSM kullanarak API ve UI'ı iki ayrı Windows Service olarak kurar. NSSM önceden kurulu olmalıdır. Üretimde araya IIS/ARR veya Nginx reverse proxy koyup TLS sertifikası kullanın.

## Kritik üretim notları
- Demo login parola doğrulamaz. Üretimde Kerberos/Windows Integrated Authentication veya Entra ID OIDC eklenmelidir.
- SQLite tek sunucu/küçük kullanım içindir. Çoklu sunucuda PostgreSQL kullanın.
- Servis hesabına Domain Admin vermeyin; yalnız hedef grupların `member` alanını değiştirme yetkisi verin.
- `Enterprise Admins` ve `Schema Admins` hard-deny'dır.
- Gerçek AD'ye geçmeden önce izole lab domain'de test edin.
