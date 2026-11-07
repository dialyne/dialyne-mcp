# Security policy

## Reporting a vulnerability
Please report security issues privately to **support@dialyne.com** (subject "Security") (do not open a public issue). Include what you found, how to reproduce it, and the impact you expect. We aim to acknowledge reports within 3 working days and keep you informed until the issue is fixed.

In scope: the hosted MCP server (`https://mcp.dialyne.com/mcp`), its OAuth endpoints, the Dialyne API and web app, and the files in this repository.

Please do not:
- place calls to numbers you do not own or to people who have not agreed to take part in your test;
- access, modify or delete data of other accounts;
- run denial-of-service or load tests, or use automated scanners that place calls.

## Credentials
- Never put an API key in a URL, a public repository, a prompt or a log. Use the `Authorization: Bearer` header and a secret store.
- If a key leaks, revoke it immediately in your Dialyne account (API keys) and create a new one. OAuth access can be revoked under Connected apps.

## Supported versions
Only the current hosted service and the latest version of this repository are supported.
