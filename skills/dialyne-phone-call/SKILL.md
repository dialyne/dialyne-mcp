---
name: dialyne-phone-call
description: Place a real phone call to a business or person in France (+33) for the user with Dialyne, then report the written result. Use when the user asks you to phone, call, ring or contact by phone someone in France - book a table, make or move an appointment, cancel or follow up an order, ask a shop or office a question. Dialyne's voice agent introduces itself as the user's virtual assistant (an AI), handles phone menus and hold, and asks you if it needs information during the call. Do not use for numbers outside France, emergencies, marketing, prospecting or mass calling.
license: MIT
compatibility: Needs the Dialyne MCP server (https://mcp.dialyne.com/mcp, OAuth or API key) or HTTPS access to the Dialyne REST API with an API key in DIALYNE_API_KEY. Calls whenever the user asks; automatic retries 08:00-21:00 in the callee's time zone.
metadata:
  author: Dialyne
  version: "1.1.0"
  homepage: https://dialyne.com
  env: DIALYNE_API_KEY (optional, for API-key access)
---

# Dialyne phone call (France)

Dialyne gives you a phone line in France. You describe a task; Dialyne's French-speaking voice agent calls the number, introduces itself as the user's virtual assistant (it never denies being an AI), navigates the phone menu, waits on hold, talks to the person, and you get back a written outcome and summary. No audio is returned.

## Before calling
1. The user must have asked for this call. If you found the number yourself (web search, memory, a document), show it to the user and get a yes first.
2. Only French numbers: `+33` followed by 9 digits (`01 42 00 00 00` → `+33142000000`). Landlines and mobiles (06/07) are fine. Never emergency or short numbers (15, 17, 18, 112, 3919…): tell the user to dial those themselves. No premium-rate numbers (081/082/088/089).
3. Never for marketing, sales prospecting, surveys, mass or repeated calling, threats, harassment or impersonation (unlawful in France). Refuse such requests; do not rephrase them to get around the rules. Codes, passwords and card details are the user's call: pass one on only when the call needs it and the user agrees, written as `[secret: value]` (masked in what Dialyne stores); for a payment, prefer `transfer_call_to_user`.
4. Collect what the callee may ask: the user's name, dates and time windows, references (booking, customer, plate number), and what is acceptable.

## Connect
- **MCP (preferred)**: server `dialyne` at `https://mcp.dialyne.com/mcp`. OAuth sign-in is automatic in Claude, ChatGPT, Cursor, VS Code, Gemini CLI. Without a browser, send `Authorization: Bearer $DIALYNE_API_KEY`. Never put the key in a URL.
- **REST (no MCP client)**: `https://api.dialyne.com/v1/...` with the same header. See the REST section below.

## Call flow with MCP tools
1. `place_phone_call(phone_number, task, language?, scheduled_at?, idempotency_key?)`
   - `task`: goal + on whose behalf + facts + limits, e.g. "Book a table for 4 on Friday around 8 pm for Martin. Any time 7:30-9 pm is fine. Indoors preferred."
   - `language`: `fr` (default), `en`, or `auto`.
   - `scheduled_at`: ISO 8601 with offset (e.g. `2026-11-03T14:00:00+01:00`) to call later, at exactly that time. Pick a time that suits the person called: Dialyne does not restrict the hours of calls the user asks for.
   - `idempotency_key`: any unique string; reuse it if you must retry after an error so the call is not placed twice.
   - It returns a `call_id` immediately. **The call is not finished.**
2. Loop: `get_call(call_id, wait_seconds=25, after_event_id=<last_event_id>)` until `done` is `true`. Each call waits up to 25 s for news, so you do not need to poll faster.
3. If `pending_question` appears, answer within 45 seconds with `answer_call_question(call_id, answer)`. Use information the user gave you; if you do not have it, ask the user right away and relay their exact words. Never invent personal data.
4. When `done` is `true`, tell the user the `outcome` and `summary`. Use `get_call(..., response_format="detailed")` if they want the transcript.

Outcomes: `success`, `failed`, `voicemail`, `no_answer`, `busy` (retried once automatically after 15 min, between 08:00 and 21:00 callee's time, free), `callback_requested`.

Other tools:
- `transfer_call_to_user(call_id, user_phone_number)`: the user wants to talk themselves and can pick up now.
- `schedule_callback(call_id, callback_at)`: call the same number again with the same task (e.g. the callee said "call back tomorrow after 3 pm").
- `cancel_call(call_id)`: the user changed their mind.
- `list_calls(query?, outcome?)`: find a past call or check a number was not called recently.
- `get_account_balance()`: minutes of conversation left.
- `hold_call_question(call_id)`: the user needs a little more time to answer a pending question; the voice agent asks the callee for one more minute (only if they agree).
- `place_batch_calls(phone_numbers, task)` and `get_batch_calls(batch_id)`: the same call to a list of numbers the user gave (Pro and Enterprise plans, 100 at most), then its results. Never for marketing or mass calling.
- `configure_agent_identity(...)`: read or change how the agent introduces itself (first name, tone, opening line, answer to "who is calling?", introduction, AI mention in the opening). Name and tone change freely. Any other change returns a warning (`responsibility_acceptance_required`) and changes nothing: show the warning to the user word for word and call again with `accept_responsibility=true` and `warning_version` only if the user explicitly accepts. Never accept it yourself. For a one-off greeting, put it in the `task` instead.

Calling hours: a call the user asks for is placed straight away or at `scheduled_at`, day or night. Automatic retries (busy line, no answer, "call back later" without a time) stay within 08:00-21:00 in the callee's time zone; when the callee gives a precise callback time, the callback is placed at that time. If a call comes back with `status: scheduled` and `scheduled_for`, tell the user when it will happen instead of waiting.

## Errors (tool results with isError)
- `insufficient_credit`: tell the user to add credit from their Dialyne account. Do not retry until they confirm.
- `task_refused`, `number_blocked`: do not retry; explain to the user.
- `invalid_phone_number`, `not_a_french_number`, `emergency_or_short_number`: ask the user for a valid French number, or tell them to dial an emergency number themselves.
- `wrong_call_state`: the call already ended; check `get_call`.
- `timeout`, `service_error`: check `list_calls` before retrying, then retry with the same `idempotency_key`.

## REST equivalent (when you cannot use MCP)
```bash
# start (French field names on the REST API)
curl -sS -X POST https://api.dialyne.com/v1/missions \
  -H "Authorization: Bearer $DIALYNE_API_KEY" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"numero": "+33534001122", "mission": "Book a table for 4 on Friday around 8 pm for Martin.", "langue": "en"}'
# follow: repeat with apres = id of the last event received, until "termine": true
curl -sS "https://api.dialyne.com/v1/missions/$ID/direct?apres=0" -H "Authorization: Bearer $DIALYNE_API_KEY"
# answer a pending question (field "question" in the previous response)
curl -sS -X POST https://api.dialyne.com/v1/missions/$ID/answer \
  -H "Authorization: Bearer $DIALYNE_API_KEY" -H "Content-Type: application/json" -d '{"reponse": "Indoors, please"}'
```
REST statuses: `planifiee`, `en_cours`, `relance_planifiee`, `terminee`, `annulee`, `erreur`; results: `reussi`, `echec`, `repondeur`, `pas_de_reponse`, `occupe`, `rappel_demande`.

More: https://dialyne.com/llms.txt · https://dialyne.com/docs/mcp · https://dialyne.com/legal/cgu
