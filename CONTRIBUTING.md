# Contributing

Thanks for helping other people connect their agents to Dialyne.

This repository contains connection files, an agent skill, examples and docs. The Dialyne service (the MCP server and the voice agent) is hosted and not open source, so issues about call quality or your account belong to support@dialyne.com, not here.

## Welcome contributions
- A configuration snippet for an MCP client that is not listed yet, tested by you.
- Fixes to examples (curl, Python, TypeScript, n8n) or new ones (LangChain, OpenAI Agents SDK, LiveKit Agents…).
- Clearer wording in the README, `llms-install.md` or the skill.

## Rules
- Never commit an API key, a token, a real phone number of a third party or a call transcript. Use `+33142000000`-style placeholders and environment variables (`DIALYNE_API_KEY`).
- Examples must keep the service rules visible: one call at a time requested by the user, AI disclosure, no marketing or mass calling.
- Keep tool names exactly as the server exposes them (`place_phone_call`, `get_call`, `answer_call_question`, `transfer_call_to_user`, `schedule_callback`, `cancel_call`, `list_calls`, `get_account_balance`, `configure_agent_identity`, `hold_call_question`, `place_batch_calls`, `get_batch_calls`).
- JSON files must stay valid; `server.json` must validate against the MCP Registry schema referenced in its `$schema`.

## Process
1. Open an issue describing the change (optional for typos).
2. Open a pull request with a short description and how you tested it.
3. A maintainer reviews it; by contributing you agree that your contribution is licensed under the MIT license of this repository.
