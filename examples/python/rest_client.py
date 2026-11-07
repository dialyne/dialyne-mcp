"""Dialyne REST API from Python (no MCP client needed). The REST API uses French field names.

    pip install httpx
    export DIALYNE_API_KEY=tel_...
    python rest_client.py +33534001122 "Book a table for 4 on Friday around 8 pm for Martin."

This places a REAL phone call: only call numbers you are allowed to call, for a task the user asked for.
"""
from __future__ import annotations

import os
import sys
import time
import uuid

import httpx

API = os.environ.get("DIALYNE_API_URL", "https://api.dialyne.com")


def main() -> None:
    phone, task = sys.argv[1], sys.argv[2]
    headers = {"Authorization": f"Bearer {os.environ['DIALYNE_API_KEY']}"}
    with httpx.Client(base_url=API, headers=headers, timeout=60) as api:
        r = api.post("/v1/missions", json={"numero": phone, "mission": task},
                     headers={"Idempotency-Key": str(uuid.uuid4())})  # safe to retry with the same key
        if r.status_code >= 400:
            sys.exit(f"refused ({r.status_code}): {r.json().get('detail')}")
        mission = r.json()
        print("call:", mission["id"], mission["statut"])
        if mission["statut"] != "en_cours":
            print("scheduled for", mission.get("planifiee_le"))
            return
        cursor = 0
        while True:
            live = api.get(f"/v1/missions/{mission['id']}/direct", params={"apres": cursor}).json()
            for event in live["evenements"]:
                cursor = event["id"]
                if event["type"] == "transcription":
                    print(f"  {event['data'].get('role')}: {event['data'].get('texte')}")
            if live.get("question"):
                answer = input(f"Voice agent asks: {live['question'].get('texte')}\n> ")  # within ~45 s
                api.post(f"/v1/missions/{mission['id']}/answer", json={"reponse": answer})
            if live["termine"]:
                print("result:", live["resultat"], "-", live["resume"])
                return
            time.sleep(3)


if __name__ == "__main__":
    main()
