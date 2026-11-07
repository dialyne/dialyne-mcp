# Install Dialyne (instructions for AI agents)

Follow these steps to give yourself (or the agent you are configuring) a real phone line in France. Dialyne places calls to French numbers (+33) and returns a written result.

## 0. What you need from your human
- A Dialyne account with a verified mobile number and some call credit. If they have none, ask them to create one at https://dialyne.com (you cannot create it for them).
- Their agreement on how you connect: OAuth sign-in (preferred when your client supports it) or an API key.

## 1. Connect over MCP with OAuth (Claude, ChatGPT, Cursor, VS Code, Le Chat…)
Add a remote MCP server with this URL and nothing else:

```
https://mcp.dialyne.com/mcp
```

Your client discovers the OAuth server by itself (RFC 9728 metadata at `https://mcp.dialyne.com/.well-known/oauth-protected-resource/mcp`), registers dynamically and opens a Dialyne sign-in page where your human signs in and clicks "Autoriser". Listing the tools works before sign-in; calling a tool triggers the sign-in.

- Claude (claude.ai, Desktop): Settings › Connectors › Add custom connector › paste the URL.
- ChatGPT: Settings › Connectors (developer mode) › Create › paste the URL, authentication "OAuth".
- Claude Code: `claude mcp add --transport http dialyne https://mcp.dialyne.com/mcp`
- Cursor (`~/.cursor/mcp.json`): `{"mcpServers": {"dialyne": {"url": "https://mcp.dialyne.com/mcp"}}}`
- VS Code (`.vscode/mcp.json`): `{"servers": {"dialyne": {"type": "http", "url": "https://mcp.dialyne.com/mcp"}}}`
- Gemini CLI (`~/.gemini/settings.json`): `{"mcpServers": {"dialyne": {"httpUrl": "https://mcp.dialyne.com/mcp"}}}`

## 2. Or connect with an API key (agents without a browser: Hermes, OpenClaw, n8n, scripts)
1. Your human opens their Dialyne account › API keys › Create key. The key starts with `tel_`. Store it as a secret (environment variable `DIALYNE_API_KEY`); never print it back in full and never put it in a URL.
2. Send it as a header on the MCP endpoint:
   - Claude Code: `claude mcp add --transport http dialyne https://mcp.dialyne.com/mcp --header "Authorization: Bearer $DIALYNE_API_KEY"`
   - Cursor: `{"mcpServers": {"dialyne": {"url": "https://mcp.dialyne.com/mcp", "headers": {"Authorization": "Bearer ${env:DIALYNE_API_KEY}"}}}}`
   - OpenAI Responses API: `{"type": "mcp", "server_label": "dialyne", "server_url": "https://mcp.dialyne.com/mcp", "headers": {"Authorization": "Bearer <key>"}, "require_approval": "always"}`
3. Or call the REST API directly:

```bash
curl -X POST https://api.dialyne.com/v1/missions \
  -H "Authorization: Bearer $DIALYNE_API_KEY" -H "Content-Type: application/json" \
  -H "Idempotency-Key: book-le-lys-001" \
  -d '{"numero": "+33534001122", "mission": "Book a table for 4 on Friday around 8 pm for Martin. Indoors preferred."}'
```

## 3. Check the connection
Call `get_account_balance`. It returns `talk_minutes_left`. If it fails with `unauthorized`, the key or sign-in is wrong; if `talk_minutes_left` is 0, ask your human to add credit from their account.

## 4. Place a call well
1. Only call when your human asked for this call. If you found the number yourself, confirm it with them first.
2. Write the task as goal + on whose behalf + facts + limits: "Book a table for 4 on Friday around 8 pm for Martin. Accept 7:30–9 pm. Indoors preferred."
3. `place_phone_call` returns a `call_id` immediately: the call is NOT finished.
4. Loop on `get_call(call_id, wait_seconds=25, after_event_id=<last_event_id>)` until `done=true`.
5. If `pending_question` appears, answer with `answer_call_question` within 45 seconds (ask your human if you do not know the answer).
6. Report `outcome` and `summary` to your human. If they want to talk themselves, offer `transfer_call_to_user`.

## Rules you must follow
- France only (+33). Calls at any time the user chooses; automatic retries stay within 08:00–21:00 (callee's time).
- Cost: 0.20 € per minute of conversation, billed per second, from your human's prepaid credit (Starter: credits valid 30 days after each top-up); busy and unanswered calls are free; the phone number is free while the account is active (https://dialyne.com/tarifs/).
- The voice agent says it is an AI calling on behalf of your human ("Hello, this is Léa, <name>'s virtual assistant"). Your human may customise how it introduces itself (`configure_agent_identity`); a deviation from the recommended settings needs their explicit acceptance of a warning, which you show them word for word. Do not ask it to hide being an AI on your own. Only exception: your human confirms the callee already knows an AI will call (`ai_disclosure: "callee_already_informed"` + `callee_informed_confirmation`, logged; see compliance.md). It never denies being an AI.
- No marketing, prospecting, surveys, mass calling, threats, harassment or impersonation (unlawful in France, refused).
- Codes and card details: your human decides. Pass one on only when the call needs it, write it as `[secret: value]` (masked in what Dialyne stores), and prefer `transfer_call_to_user` for a payment.
- If the person asks not to be called again, the number is blocked for every Dialyne customer.

More: https://dialyne.com/llms.txt · https://dialyne.com/docs/mcp · https://dialyne.com/legal/cgu
