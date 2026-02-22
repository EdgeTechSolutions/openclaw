import https from "https";

interface GmailMessage {
  id: string;
  threadId: string;
  labelIds?: string[];
  snippet?: string;
  payload?: {
    headers: { name: string; value: string }[];
    body?: { data?: string };
    parts?: any[];
  };
  sizeEstimate?: number;
  historyId?: string;
  internalDate?: string;
}

interface GmailListResponse {
  messages: { id: string; threadId: string }[];
  nextPageToken?: string;
  resultSizeEstimate: number;
}

interface GmailLabel {
  id: string;
  name: string;
  type: string;
  messageListVisibility?: string;
  labelListVisibility?: string;
}

class GmailClient {
  private token: string;
  private email: string;

  constructor(token: string, email: string) {
    this.token = token;
    this.email = email;
  }

  private async request(path: string, query?: Record<string, string>, options?: { method?: string; headers?: Record<string, string>; body?: string }): Promise<any> {
    const reqUrl = new URL(`https://www.googleapis.com/gmail/v1/users/${this.email}${path}`);
    if (query) {
      Object.entries(query).forEach(([k, v]) => reqUrl.searchParams.append(k, v));
    }

    const fetchOptions: RequestInit = {
      method: options?.method || "GET",
      headers: { Authorization: `Bearer ${this.token}`, ...options?.headers },
    };
    if (options?.body) fetchOptions.body = options.body;

    const res = await fetch(reqUrl.toString(), fetchOptions);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status}: ${text}`);
    }
    return res.json();
  }

  async listMessages(query = "in:inbox", maxResults = 10): Promise<GmailListResponse> {
    return this.request("/messages", { q: query, maxResults: maxResults.toString() });
  }

  async getMessage(id: string, format = "full"): Promise<GmailMessage> {
    return this.request(`/messages/${id}`, { format });
  }

  async getMessageText(id: string): Promise<string> {
    const msg = await this.request(`/messages/${id}`, { format: "full" });
    if (msg.payload.parts) {
      const textPart = msg.payload.parts.find((p: any) => p.mimeType === "text/plain");
      if (textPart?.body?.data) {
        return Buffer.from(textPart.body.data, "base64").toString("utf-8");
      }
    }
    if (msg.payload.body?.data) {
      return Buffer.from(msg.payload.body.data, "base64").toString("utf-8");
    }
    return msg.snippet || "";
  }

  async listLabels(): Promise<GmailLabel[]> {
    return this.request("/labels");
  }

  async sendMessage(to: string, subject: string, body: string): Promise<any> {
    const raw = `To: ${to}\r\nSubject: ${subject}\r\n\r\n${body}`;
    const encoded = Buffer.from(raw).toString("base64").replace(/\+/g, "-").replace(/\//g, "_");
    return this.request("/messages/send", {}, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw: encoded }),
    });
  }
}

// CLI

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // Load token
  const fs = require("fs");
  const tokenPath = "/workspace/.config/gogcli/tokens/token-luka.stopar@gmail.com.json";
  const tokenData = JSON.parse(fs.readFileSync(tokenPath, "utf-8"));
  const client = new GmailClient(tokenData.access_token, "luka@stopar.si");

  switch (command) {
    case "list": {
      const query = args[1] || "in:inbox";
      const max = parseInt(args[2]) || 5;
      const res = await client.listMessages(query, max);
      for (const m of res.messages) {
        const msg = await client.getMessage(m.id);
        const subject = msg.payload?.headers?.find((h) => h.name === "Subject")?.value || "No Subject";
        const from = msg.payload?.headers?.find((h) => h.name === "From")?.value || "Unknown";
        console.log(`[${msg.id.slice(0, 8)}] ${subject} (${from})`);
      }
      break;
    }
    case "read": {
      const id = args[1];
      if (!id) { console.error("Usage: gmail read <message-id>"); process.exit(1); }
      const text = await client.getMessageText(id);
      console.log(text);
      break;
    }
    case "search": {
      const query = args.slice(1).join(" ");
      const res = await client.listMessages(query, 10);
      for (const m of res.messages) {
        const msg = await client.getMessage(m.id);
        const subject = msg.payload?.headers?.find((h) => h.name === "Subject")?.value || "No Subject";
        const from = msg.payload?.headers?.find((h) => h.name === "From")?.value || "Unknown";
        console.log(`[${msg.id.slice(0, 8)}] ${subject} (${from})`);
      }
      break;
    }
    case "labels": {
      const labels = await client.listLabels();
      for (const l of labels) {
        console.log(`${l.id.padEnd(20)} ${l.name}`);
      }
      break;
    }
    case "send": {
      const to = args[1];
      const subject = args[2];
      const body = args.slice(3).join(" ");
      if (!to || !subject) { console.error("Usage: gmail send <to> <subject> <body>"); process.exit(1); }
      await client.sendMessage(to, subject, body);
      console.log("✅ Email sent");
      break;
    }
    default:
      console.log(`Usage: gmail <command>

Commands:
  list [query] [max]    List messages (default: in:inbox 5)
  read <id>            Read message text
  search <query>       Search messages
  labels               List labels
  send <to> <subj> <body>  Send email`);
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});