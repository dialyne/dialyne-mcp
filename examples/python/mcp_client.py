"""Dialyne over MCP from Python (official `mcp` SDK, Streamable HTTP, API key in a header).

    pip install "mcp>=1.10"
    export DIALYNE_API_KEY=tel_...            # from your Dialyne account › API keys
    python mcp_client.py                        # lists the tools and shows your balance
    python mcp_client.py +33534001122 "Book a table for 4 on Friday around 8 pm for Martin."

The second form places a REAL phone call: only call numbers you are allowed to call, for a task the user asked for.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("DIALYNE_MCP_URL", "https://mcp.dialyne.com/mcp")


def data(result) -> dict:
    """Structured result of a tool call (raises on isError, with the server's actionable message)."""
    if result.isError:
        raise RuntimeError(result.content[0].text if result.content else "tool error")
    if result.structuredContent is not None:
        return result.structuredContent
    return json.loads(result.content[0].text)


async def main() -> None:
    headers = {"Authorization": f"Bearer {os.environ['DIALYNE_API_KEY']}"}
    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", ", ".join(t.name for t in tools.tools))
            print("balance:", data(await session.call_tool("get_account_balance", {})))
            if len(sys.argv) < 3:
                return
            phone, task = sys.argv[1], sys.argv[2]
            call = data(await session.call_tool("place_phone_call", {
                "phone_number": phone, "task": task, "idempotency_key": str(uuid.uuid4())}))
            print("call:", call["call_id"], call["status"])
            if call["status"] != "in_progress":
                print(call.get("next_step"))
                return
            cursor = 0
            while True:
                state = data(await session.call_tool("get_call", {
                    "call_id": call["call_id"], "wait_seconds": 25, "after_event_id": cursor}))
                cursor = state["last_event_id"]
                for event in state.get("events", []):
                    print("  event:", event["type"], event.get("state", ""))
                if state.get("pending_question"):
                    q = state["pending_question"]
                    answer = input(f"Voice agent asks: {q['text']}\n> ")  # answer within ~45 s
                    data(await session.call_tool("answer_call_question", {
                        "call_id": call["call_id"], "answer": answer, "question_id": q["question_id"]}))
                if state["done"]:
                    print("outcome:", state.get("outcome"), "-", state.get("summary", ""))
                    return


if __name__ == "__main__":
    asyncio.run(main())
