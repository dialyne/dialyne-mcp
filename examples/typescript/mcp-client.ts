/**
 * Dialyne over MCP from TypeScript (official @modelcontextprotocol/sdk, Streamable HTTP, API key in a header).
 *
 *   npm install
 *   export DIALYNE_API_KEY=tel_...
 *   npx tsx mcp-client.ts                                   # lists the tools and shows your balance
 *   npx tsx mcp-client.ts +33534001122 "Book a table for 4 on Friday around 8 pm for Martin."
 *
 * The second form places a REAL phone call: only call numbers you are allowed to call, for a task the user asked for.
 */
import { randomUUID } from "node:crypto";
import { createInterface } from "node:readline/promises";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const MCP_URL = process.env.DIALYNE_MCP_URL ?? "https://mcp.dialyne.com/mcp";

type ToolResult = { isError?: boolean; structuredContent?: unknown; content?: Array<{ type: string; text?: string }> };

function data<T = Record<string, any>>(result: ToolResult): T {
  const text = result.content?.find((c) => c.type === "text")?.text ?? "";
  if (result.isError) throw new Error(text || "tool error"); // actionable message from the server
  return (result.structuredContent ?? JSON.parse(text)) as T;
}

async function main(): Promise<void> {
  const transport = new StreamableHTTPClientTransport(new URL(MCP_URL), {
    requestInit: { headers: { Authorization: `Bearer ${process.env.DIALYNE_API_KEY}` } },
  });
  const client = new Client({ name: "dialyne-example", version: "1.0.0" });
  await client.connect(transport);
  try {
    const { tools } = await client.listTools();
    console.log("tools:", tools.map((t) => t.name).join(", "));
    console.log("balance:", data(await client.callTool({ name: "get_account_balance", arguments: {} }) as ToolResult));

    const [phone, task] = process.argv.slice(2);
    if (!phone || !task) return;
    const call = data(await client.callTool({
      name: "place_phone_call",
      arguments: { phone_number: phone, task, idempotency_key: randomUUID() },
    }) as ToolResult);
    console.log("call:", call.call_id, call.status);
    if (call.status !== "in_progress") return console.log(call.next_step);

    const rl = createInterface({ input: process.stdin, output: process.stdout });
    let cursor = 0;
    for (;;) {
      const state = data(await client.callTool({
        name: "get_call",
        arguments: { call_id: call.call_id, wait_seconds: 25, after_event_id: cursor },
      }) as ToolResult);
      cursor = state.last_event_id;
      for (const event of state.events ?? []) console.log("  event:", event.type, event.state ?? "");
      if (state.pending_question) {
        const answer = await rl.question(`Voice agent asks: ${state.pending_question.text}\n> `); // within ~45 s
        data(await client.callTool({
          name: "answer_call_question",
          arguments: { call_id: call.call_id, answer, question_id: state.pending_question.question_id },
        }) as ToolResult);
      }
      if (state.done) {
        console.log("outcome:", state.outcome, "-", state.summary ?? "");
        break;
      }
    }
    rl.close();
  } finally {
    await client.close();
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
