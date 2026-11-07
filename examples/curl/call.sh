#!/usr/bin/env bash
# Call a French number with the Dialyne REST API and follow the call until it ends.
#   export DIALYNE_API_KEY=tel_...
#   ./call.sh +33534001122 "Book a table for 4 on Friday around 8 pm for Martin."
# This places a REAL phone call: only call numbers you are allowed to call, for a task the user asked for.
# Requires: curl, jq, uuidgen.
set -euo pipefail
API="${DIALYNE_API_URL:-https://api.dialyne.com}"
AUTH="Authorization: Bearer ${DIALYNE_API_KEY:?set DIALYNE_API_KEY}"
NUMBER="${1:?phone number, e.g. +33534001122}"
TASK="${2:?task in plain language}"

# 1. Start the call. The Idempotency-Key makes a retry return the same call instead of calling twice.
MISSION=$(curl -sS -X POST "$API/v1/missions" -H "$AUTH" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d "$(jq -n --arg n "$NUMBER" --arg m "$TASK" '{numero: $n, mission: $m}')")
ID=$(echo "$MISSION" | jq -r '.id // empty')
[ -n "$ID" ] || { echo "refused: $(echo "$MISSION" | jq -r '.detail')"; exit 1; }
echo "call $ID: $(echo "$MISSION" | jq -r '.statut')"

# 2. Follow it: new events since the last id, until "termine" is true.
AFTER=0
while true; do
  LIVE=$(curl -sS "$API/v1/missions/$ID/direct?apres=$AFTER" -H "$AUTH")
  echo "$LIVE" | jq -r '.evenements[] | select(.type=="transcription") | "  \(.data.role): \(.data.texte)"'
  AFTER=$(echo "$LIVE" | jq -r '[.evenements[].id] | max // '"$AFTER")
  QUESTION=$(echo "$LIVE" | jq -r '.question.texte // empty')
  if [ -n "$QUESTION" ]; then
    read -r -p "Voice agent asks: $QUESTION > " ANSWER   # answer within ~45 s
    curl -sS -X POST "$API/v1/missions/$ID/answer" -H "$AUTH" -H "Content-Type: application/json" \
      -d "$(jq -n --arg r "$ANSWER" '{reponse: $r}')" > /dev/null
  fi
  if [ "$(echo "$LIVE" | jq -r '.termine')" = "true" ]; then
    echo "result: $(echo "$LIVE" | jq -r '.resultat') - $(echo "$LIVE" | jq -r '.resume')"
    break
  fi
  sleep 3
done
