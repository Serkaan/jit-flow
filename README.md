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
Reason:
