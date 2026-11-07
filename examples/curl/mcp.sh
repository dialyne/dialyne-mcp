#!/usr/bin/env bash
# Talk to the Dialyne MCP server with raw JSON-RPC (Streamable HTTP). Useful to check a connection.
#   ./mcp.sh            # tools/list works without credentials
#   DIALYNE_API_KEY=tel_... ./mcp.sh balance
set -euo pipefail
MCP="${DIALYNE_MCP_URL:-https://mcp.dialyne.com/mcp}"
H=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream")

if [ "${1:-}" = "balance" ]; then
  curl -sS -X POST "$MCP" "${H[@]}" -H "Authorization: Bearer ${DIALYNE_API_KEY:?set DIALYNE_API_KEY}" \
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_account_balance","arguments":{}}}' | jq '.result.structuredContent'
else
  curl -sS -X POST "$MCP" "${H[@]}" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq -r '.result.tools[] | "\(.name): \(.title)"'
fi
# Without credentials, tools/call answers HTTP 401 with
#   WWW-Authenticate: Bearer resource_metadata="https://mcp.dialyne.com/.well-known/oauth-protected-resource/mcp"
# which is how MCP clients discover the OAuth sign-in.
