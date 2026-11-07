# Examples

All examples read the API key from `DIALYNE_API_KEY` (create one in your Dialyne account › API keys). Never hard-code a key or put it in a URL.

Examples that start a call place a **real phone call** to the number you give: only call numbers you are allowed to call, for a task the user asked for. Calls are placed whenever you ask, day or night, so choose a suitable time for the person called; automatic retries stay within 08:00–21:00 in the callee's time zone, and a callback time the callee asks for is kept.

| Folder | What | Run |
|---|---|---|
| [`curl/`](curl/) | `mcp.sh`: list the MCP tools (no key needed) and check your balance. `call.sh`: start a call over REST and follow it | `./mcp.sh`, `./call.sh +33… "task"` |
| [`python/`](python/) | `mcp_client.py`: official MCP SDK over Streamable HTTP. `rest_client.py`: REST with httpx | `pip install -r requirements.txt` then `python mcp_client.py` |
| [`typescript/`](typescript/) | `mcp-client.ts`: official `@modelcontextprotocol/sdk` | `npm install && npx tsx mcp-client.ts` |
| [`n8n/`](n8n/) | Workflow to import: start a call, poll every 20 s, output the result | Import the JSON, create a "Header Auth" credential named `Dialyne API key` (`Authorization` / `Bearer tel_…`) |

MCP tool names: `place_phone_call`, `get_call`, `answer_call_question`, `transfer_call_to_user`, `schedule_callback`, `cancel_call`, `list_calls`, `get_account_balance`, `configure_agent_identity`. The REST API uses French field names (`numero`, `mission`, `statut`, `resultat`, `resume`); reference: https://dialyne.com/docs/tools.md and https://api.dialyne.com/openapi.json.

For calls scheduled hours ahead, prefer webhooks (`webhook_url` on the mission, signed with HMAC-SHA256) over polling.
