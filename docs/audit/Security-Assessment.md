# Security Assessment

**Score: 70/100 — PARTIALLY VERIFIED**

---

## 1. Authentication

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| JWT Bearer | ✅ Implemented | `app/auth/jwt.py` — HS256 token creation and validation |
| API Key | ✅ Implemented | `x-api-key` header checked in `app/auth/dependencies.py` |
| Demo Login | ✅ Implemented | `POST /api/v1/auth/demo-login` — returns JWT |
| Email/Password | ✅ Implemented | `POST /api/v1/auth/register` + `POST /api/v1/auth/login` — salted SHA-256 |

**Finding — MEDIUM:** Password hashing uses SHA-256 with salt (custom implementation) instead of bcrypt/argon2. While functional for MVP, this is not enterprise-grade password storage.

**Evidence:** `app/services/store.py:56-58` — `hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()`

## 2. Authorization

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| Role-based | ⚠️ Implemented | `app/auth/dependencies.py:23-34` — `require_role()` decorator exists. Only used on admin endpoints. |
| Tenant isolation | ✅ Implemented | Tenant middleware extracts tenant from context. All repository queries filter by tenant_id. |
| Route protection | ⚠️ Partial | Some routes use `get_current_user()` with `auto_error=False`, defaults to anonymous. Query endpoint explicitly rejects anonymous but other endpoints may not. |

**Finding — MEDIUM:** RBAC exists but is minimally enforced. Only admin endpoints check roles. Most endpoints accept any authenticated user.

## 3. SQL Injection Protection — VERIFIED

The system has comprehensive SQL injection protection at multiple layers:

| Layer | Protection | Evidence |
|-------|-----------|----------|
| Generator | sqlglot identifier quoting | `ke/services/generator.py:35-36` — `_safe_identifier()` uses `E.to_identifier()` |
| Generator | sqlglot value quoting | `ke/services/generator.py:30-32` — `_safe_quote()` escapes single quotes |
| Generator | Operator whitelist | `ke/services/generator.py:27` — `_SAFE_OPS` set of allowed operators |
| Executor | sqlglot parse validation | `ke/services/executor.py:59` — `sqlglot.parse_one()` before EXPLAIN |
| Policy L2 | SQL sanitization | `ke/services/policy/layers.py` — L2 SanitizationLayer |
| Policy L5 | SQL validation | `ke/services/policy/layers.py` — L5 SQL Validation Layer |

**Finding — VERIFIED:** This is genuinely well-done. All SQL injection vectors identified in the security audit have been addressed.

## 4. Prompt Injection Protection

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| Input sanitization | ⚠️ Partial | Query text is passed directly to the LLM. No prompt injection detection before generation. |
| Output validation | ✅ Implemented | L2-L10 guardrails validate generated SQL. L6 Read-Only enforcement blocks DML/DDL. |
| Prompt templates | ⚠️ Partial | Templates include schema context and user query. No structural separation between instruction and user input. |

**Finding — HIGH:** The system does not have prompt injection detection on user input before it reaches the LLM. The guardrails validate the OUTPUT (generated SQL), not the INPUT (user query). An attacker could craft a prompt injection payload that bypasses the intent classifier.

## 5. OWASP Top 10 Coverage

| Risk | Status | Evidence |
|------|--------|----------|
| A01: Broken Access Control | ⚠️ Partial | Tenant isolation exists. RBAC is minimal. |
| A02: Cryptographic Failures | ⚠️ Partial | JWT uses HS256 (acceptable). Passwords use SHA-256 (should be bcrypt). |
| A03: Injection | ✅ Verified | SQL injection covered. Prompt injection partially covered. |
| A04: Insecure Design | ⚠️ Partial | In-memory state stores are insecure for production. |
| A05: Security Misconfiguration | ✅ Good | CORS configured, rate limiting, structured logging. |
| A06: Vulnerable Components | ⚠️ Partial | No dependency scanning in CI. Trivy + pip-audit configured but never run. |
| A07: Auth Failures | ⚠️ Partial | JWT + API key + email/password. SSO missing. |
| A08: Data Integrity | ⚠️ Partial | Audit logging exists. Immutable audit chain not implemented. |
| A09: Logging & Monitoring | ✅ Good | Structured JSON logging, request ID, health endpoints. |
| A10: SSRF | ❌ Not assessed | No testing for server-side request forgery in connectors. |

## 6. Realistic Attack Paths

1. **Prompt Injection via Query Input** → Bypass intent classifier → Generate malicious SQL → **Mitigated by L2-L10 guardrails** (SQL validated before execution)
2. **Brute Force Auth** → No rate limiting on login → **Mitigated by global rate limiter** (100 req/min)
3. **Stale JWT Token** → No refresh/revocation → Token valid until expiry (default 1 hour)
4. **Cross-Tenant Data Access** → RLS in PostgreSQL prevents this → **Verified**
5. **Injection via DB Connector** → Connectors extract schema data → SQL is read-only SELECT → **Low risk**

## 7. Attack Surface Summary

| Surface | Exposure | Risk |
|---------|----------|------|
| Public API (port 8100) | Internet-facing | HIGH — primary attack vector |
| KE API (port 8200) | Internal only | LOW — service token protected |
| PostgreSQL (port 5432) | Docker network | LOW — not exposed externally |
| Qdrant (port 6333) | Docker network | LOW — not exposed externally |
| Redis (port 6379) | Docker network | LOW — not exposed externally |

**Security Verdict: 70/100 — Good security fundamentals. SQL injection protection is excellent. Prompt injection and password hashing need improvement for enterprise readiness.**
