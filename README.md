# 🔐 JIT-Flow

AI-Assisted Just-In-Time Access Management (JIT PAM) for Active Directory.

JIT-Flow enables organizations to grant temporary privileged access with approval workflows, AI-assisted risk analysis, audit logging, and automatic access revocation.

---

## 🚀 Key Features

✅ Temporary Active Directory Group Membership

✅ Manager Approval Workflow

✅ AI-Assisted Risk Scoring

✅ Automatic Access Revocation

✅ LDAP / LDAPS Integration

✅ Audit Logging

✅ Streamlit Web Interface

✅ FastAPI REST API

✅ Windows Service Deployment

✅ Docker Support

✅ Scheduler Based Auto-Revoke

✅ Just-In-Time Privileged Access

---

## 🎯 Why JIT-Flow?

Many organizations permanently assign privileged permissions such as:

- Domain Admins
- Backup Operators
- SQL Administrators
- Server Operators
- Local Administrators

These privileges are often forgotten after operational tasks are completed.

JIT-Flow applies the principle of least privilege:

- Right User
- Right Access
- Right Duration
- Right Approval

while ensuring elevated permissions are automatically removed when their approved duration expires.

---

## 🏗 Architecture

```text
+------------------+
| User Portal      |
+------------------+
          |
          v
+------------------+
| Approval Workflow|
+------------------+
          |
          v
+------------------+
| Risk Engine      |
+------------------+
          |
          v
+------------------+
| Active Directory |
+------------------+
          |
          v
+------------------+
| Auto Revoke      |
+------------------+
          |
          v
+------------------+
| Audit Trail      |
+------------------+
```

---

## 🔄 Access Lifecycle

```text
User Requests Access
          ↓
Risk Analysis
          ↓
Manager Approval
          ↓
Access Granted
          ↓
Timer Starts
          ↓
Access Automatically Revoked
          ↓
Audit Record Created
```

---

## 💻 Windows 11 Quick Start

### PowerShell

```powershell
Set-ExecutionPolicy -Scope Process Bypass

.\scripts\install_windows.ps1

.\.venv\Scripts\python.exe run_all.py
```

If the browser does not open automatically:

### User Interface

```text
http://127.0.0.1:8501
```

### API Documentation

```text
http://127.0.0.1:8080/docs
```

---

## 👤 Demo Accounts

| Username | Role |
|----------|------|
| requester | Requester |
| manager | Manager |
| admin | Administrator |

For development mode, any password is accepted.

> Demo authentication is intended for local testing only.

---

## 📋 Usage

### 1. Create a Request

Login as:

```text
requester
```

Create an access request.

Example:

```text
User: ahmet
Group: Domain Admins
Duration: 120 minutes
Reason: Emergency security patch
```

---

### 2. Approve Request

Logout and login as:

```text
manager
```

Open:

```text
Approval Center
```

Review risk information and approve the request.

---

### 3. Access Becomes Active

The user is added to the requested Active Directory group.

Status:

```text
Pending
↓
Active
```

---

### 4. Automatic Revocation

When the approved duration expires:

```text
Domain Admins
↓
User Removed
```

Status:

```text
Active
↓
Expired
```

---

### 5. Audit Logging

Every action is logged:

```text
REQUEST_CREATED
APPROVED
REJECTED
AD_GRANT_SUCCESS
AD_REVOKE_SUCCESS
REVOKE_CRITICAL
```

---

## 🤖 AI Risk Analysis

JIT-Flow evaluates:

- Requested group
- Access duration
- Justification quality
- Prompt injection attempts
- Restricted groups
- Privilege level

Example:

```text
Helpdesk Readers
Risk: LOW

Domain Admins
Risk: HIGH

Enterprise Admins
Risk: BLOCKED
```

---

## 🔒 Security Controls

### Protected Groups

Examples:

- Domain Admins
- Backup Operators
- Server Operators
- DNS Admins

Maximum duration:

```text
120 minutes
```

---

### Restricted Groups

The following groups are intentionally blocked:

- Enterprise Admins
- Schema Admins

Requests are automatically denied.

---

### Separation of Duties

Requesters cannot approve their own requests.

High-risk requests require explicit risk acknowledgement.

---

## 🔌 Active Directory Modes

### Development Mode

```env
AD_MODE=fake
```

Uses an in-memory fake Active Directory.

No real AD connection is required.

---

### LDAP / LDAPS Mode

```env
AD_MODE=ldap
```

Configure:

```env
AD_SERVER=
AD_PORT=
AD_BIND_DN=
AD_BIND_PASSWORD=
AD_BASE_DN=
```

in the `.env` file.

---

## 🐳 Docker Deployment

```bash
docker compose up -d
```

Services:

```text
API  -> Port 8080
UI   -> Port 8501
```

---

## ⚙ Windows Service Deployment

JIT-Flow can run as Windows Services using NSSM.

Install:

```powershell
.\scripts\install_service.ps1
```

This creates:

```text
JITFlow-API
JITFlow-UI
```

which start automatically with Windows.

---

## 📊 Current Project Status

### Implemented

✅ FastAPI Backend

✅ Streamlit User Interface

✅ Approval Workflow

✅ Audit Logging

✅ Risk Engine

✅ LDAP Integration

✅ Auto-Revoke Scheduler

✅ Docker Support

✅ Windows Service Support

---

### Planned

- Microsoft Teams Approval
- Email Approval Workflow
- Microsoft Entra ID Integration
- Windows SSO
- PostgreSQL Backend
- ServiceNow Integration
- Microsoft Sentinel Integration
- Dashboard & Reporting

---

## 🛡 Production Recommendations

Before production deployment:

- Replace demo authentication with Windows SSO or Entra ID
- Use LDAPS with certificate validation
- Store secrets securely
- Replace SQLite with PostgreSQL
- Deploy behind IIS / Nginx reverse proxy
- Enable HTTPS with valid certificates
- Delegate minimal AD permissions to the service account

Never grant Domain Admin privileges to the JIT-Flow service account.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

Created by Serkan CATALTAS

Managed Services • Identity Security • Just-In-Time Access Management
``
