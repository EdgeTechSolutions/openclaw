import https from "https";

// ── Types ──

interface Trading212Config {
  apiKeyId: string;
  secretKey: string;
  environment?: "live" | "demo";
}

interface AccountSummary {
  cash: { availableToTrade: number; inPies: number; reservedForOrders: number };
  currency: string;
  id: number;
  investments: { currentValue: number; realizedProfitLoss: number; totalCost: number; unrealizedProfitLoss: number };
  totalValue: number;
}

interface AccountCash {
  free: number;
  total: number;
  ppl: number;
  result: number;
  invested: number;
  pieCash: number;
  blocked: number;
}

interface Position {
  averagePricePaid: number;
  createdAt: string;
  currentPrice: number;
  instrument: { ticker: string; name: string; isin: string; currency: string };
  quantity: number;
  quantityAvailableForTrading: number;
  quantityInPies: number;
  walletImpact: { currency: string; totalCost: number; currentValue: number; unrealizedProfitLoss: number; fxImpact: number };
}

interface Order {
  id: number;
  ticker: string;
  type: string;
  status: string;
  quantity: number;
  limitPrice?: number;
  stopPrice?: number;
  filledQuantity?: number;
  filledValue?: number;
  createdAt?: string;
}

interface LimitOrderRequest {
  ticker: string;
  quantity: number;
  limitPrice: number;
  timeValidity?: "Day" | "GTC";
}

interface MarketOrderRequest {
  ticker: string;
  quantity: number;
}

interface StopOrderRequest {
  ticker: string;
  quantity: number;
  stopPrice: number;
  timeValidity?: "Day" | "GTC";
}

interface StopLimitOrderRequest {
  ticker: string;
  quantity: number;
  stopPrice: number;
  limitPrice: number;
  timeValidity?: "Day" | "GTC";
}

interface PaginatedResponse<T> {
  items: T[];
  nextPagePath: string | null;
}

interface HistoricalOrder {
  id: number;
  ticker: string;
  type: string;
  status: string;
  quantity: number;
  filledQuantity: number;
  filledValue: number;
  dateCreated: string;
  dateModified: string;
}

interface Dividend {
  ticker: string;
  amount: number;
  paidOn: string;
  quantity: number;
  reference: string;
}

interface Transaction {
  amount: number;
  dateTime: string;
  reference: string;
  type: string;
}

interface Exchange {
  id: number;
  name: string;
  workingSchedules: any[];
}

interface Instrument {
  addedOn: string;
  currencyCode: string;
  extendedHours: boolean;
  isin: string;
  maxOpenQuantity: number;
  name: string;
  shortName: string;
  ticker: string;
  type: string;
  workingScheduleId: number;
}

// ── HTTP Client ──

function request(
  method: string,
  url: string,
  auth: { username: string; password: string },
  body?: any
): Promise<any> {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const options: https.RequestOptions = {
      hostname: parsed.hostname,
      path: parsed.pathname + parsed.search,
      method,
      headers: {
        Authorization: "Basic " + Buffer.from(`${auth.username}:${auth.password}`).toString("base64"),
        "Content-Type": "application/json",
      },
    };

    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        if (res.statusCode && res.statusCode >= 400) {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          return;
        }
        if (!data || data.trim() === "") {
          resolve(null);
          return;
        }
        try {
          resolve(JSON.parse(data));
        } catch {
          reject(new Error(`Invalid JSON: ${data.slice(0, 200)}`));
        }
      });
    });
    req.on("error", reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// ── Client ──

export class Trading212Client {
  private auth: { username: string; password: string };
  private baseUrl: string;

  constructor(config: Trading212Config) {
    this.auth = { username: config.apiKeyId, password: config.secretKey };
    const env = config.environment || "live";
    this.baseUrl = `https://${env}.trading212.com/api/v0`;
  }

  static fromFile(path = "/workspace/.trading212-config.json"): Trading212Client {
    const fs = require("fs");
    const config = JSON.parse(fs.readFileSync(path, "utf-8"));
    return new Trading212Client({
      apiKeyId: config.apiKeyId,
      secretKey: config.secretKey,
      environment: config.environment || "live",
    });
  }

  private get(path: string) {
    return request("GET", `${this.baseUrl}${path}`, this.auth);
  }

  private post(path: string, body: any) {
    return request("POST", `${this.baseUrl}${path}`, this.auth, body);
  }

  private del(path: string) {
    return request("DELETE", `${this.baseUrl}${path}`, this.auth);
  }

  // ── Accounts ──

  async getAccountSummary(): Promise<AccountSummary> {
    return this.get("/equity/account/summary");
  }

  async getAccountCash(): Promise<AccountCash> {
    return this.get("/equity/account/cash");
  }

  // ── Positions ──

  async getPositions(ticker?: string): Promise<Position[]> {
    const query = ticker ? `?ticker=${encodeURIComponent(ticker)}` : "";
    return this.get(`/equity/positions${query}`);
  }

  // ── Orders ──

  async getPendingOrders(): Promise<Order[]> {
    return this.get("/equity/orders");
  }

  async getOrderById(orderId: number): Promise<Order> {
    return this.get(`/equity/orders/${orderId}`);
  }

  async placeLimitOrder(order: LimitOrderRequest): Promise<Order> {
    return this.post("/equity/orders/limit", {
      ticker: order.ticker,
      quantity: order.quantity,
      limitPrice: order.limitPrice,
      timeValidity: order.timeValidity || "GTC",
    });
  }

  async placeMarketOrder(order: MarketOrderRequest): Promise<Order> {
    return this.post("/equity/orders/market", {
      ticker: order.ticker,
      quantity: order.quantity,
    });
  }

  async placeStopOrder(order: StopOrderRequest): Promise<Order> {
    return this.post("/equity/orders/stop", {
      ticker: order.ticker,
      quantity: order.quantity,
      stopPrice: order.stopPrice,
      timeValidity: order.timeValidity || "GTC",
    });
  }

  async placeStopLimitOrder(order: StopLimitOrderRequest): Promise<Order> {
    return this.post("/equity/orders/stop_limit", {
      ticker: order.ticker,
      quantity: order.quantity,
      stopPrice: order.stopPrice,
      limitPrice: order.limitPrice,
      timeValidity: order.timeValidity || "GTC",
    });
  }

  async cancelOrder(orderId: number): Promise<void> {
    await this.del(`/equity/orders/${orderId}`);
  }

  // ── Instruments ──

  async getExchanges(): Promise<Exchange[]> {
    return this.get("/equity/metadata/exchanges");
  }

  async getInstruments(): Promise<Instrument[]> {
    return this.get("/equity/metadata/instruments");
  }

  // ── Historical Events ──

  async getHistoricalOrders(limit = 20, cursor?: string): Promise<PaginatedResponse<HistoricalOrder>> {
    let path = `/equity/history/orders?limit=${limit}`;
    if (cursor) path += `&cursor=${encodeURIComponent(cursor)}`;
    return this.get(path);
  }

  async getDividends(limit = 20, cursor?: string): Promise<PaginatedResponse<Dividend>> {
    let path = `/equity/history/dividends?limit=${limit}`;
    if (cursor) path += `&cursor=${encodeURIComponent(cursor)}`;
    return this.get(path);
  }

  async getTransactions(limit = 20, cursor?: string): Promise<PaginatedResponse<Transaction>> {
    let path = `/equity/history/transactions?limit=${limit}`;
    if (cursor) path += `&cursor=${encodeURIComponent(cursor)}`;
    return this.get(path);
  }

  async requestReport(
    dataIncluded: { includeDividends: boolean; includeInterest: boolean; includeOrders: boolean; includeTransactions: boolean },
    timeFrom: string,
    timeTo: string
  ): Promise<any> {
    return this.post("/equity/history/exports", { dataIncluded, timeFrom, timeTo });
  }

  async getReports(): Promise<any[]> {
    return this.get("/equity/history/exports");
  }

  // ── Pies (Deprecated) ──

  async getPies(): Promise<any[]> {
    return this.get("/equity/pies");
  }

  async getPie(pieId: number): Promise<any> {
    return this.get(`/equity/pies/${pieId}`);
  }
}

// ── CLI ──

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === "--help") {
    console.log(`Usage: trading212 <command>

Commands:
  summary              Account summary (balance, investments, P&L)
  cash                 Cash balance details
  positions            All open positions
  position <ticker>    Single position by ticker
  orders               Pending orders
  order <id>           Get order by ID
  cancel <id>          Cancel pending order
  history-orders       Historical orders
  dividends            Dividend history
  transactions         Transaction history
  instruments          List all instruments
  exchanges            List exchanges
  reports              List generated reports

Order placement (use with caution):
  buy-market <ticker> <qty>
  sell-market <ticker> <qty>
  buy-limit <ticker> <qty> <price>
  sell-limit <ticker> <qty> <price>
  buy-stop <ticker> <qty> <stopPrice>
  sell-stop <ticker> <qty> <stopPrice>
  buy-stop-limit <ticker> <qty> <stopPrice> <limitPrice>
  sell-stop-limit <ticker> <qty> <stopPrice> <limitPrice>

Note: For sell orders, quantity is automatically negated.`);
    return;
  }

  const client = Trading212Client.fromFile();

  switch (command) {
    case "summary": {
      const s = await client.getAccountSummary();
      console.log(`Account #${s.id} (${s.currency})`);
      console.log(`  Total Value:       ${s.totalValue.toFixed(2)}`);
      console.log(`  Cash Available:    ${s.cash.availableToTrade.toFixed(2)}`);
      console.log(`  Cash in Pies:      ${s.cash.inPies.toFixed(2)}`);
      console.log(`  Reserved:          ${s.cash.reservedForOrders.toFixed(2)}`);
      console.log(`  Invested (cost):   ${s.investments.totalCost.toFixed(2)}`);
      console.log(`  Current Value:     ${s.investments.currentValue.toFixed(2)}`);
      console.log(`  Unrealized P/L:    ${s.investments.unrealizedProfitLoss.toFixed(2)}`);
      console.log(`  Realized P/L:      ${s.investments.realizedProfitLoss.toFixed(2)}`);
      break;
    }
    case "cash": {
      const c = await client.getAccountCash();
      console.log(JSON.stringify(c, null, 2));
      break;
    }
    case "positions": {
      const positions = await client.getPositions();
      if (!positions.length) { console.log("No open positions."); break; }
      const sorted = positions.sort((a, b) => (b.walletImpact?.currentValue ?? 0) - (a.walletImpact?.currentValue ?? 0));
      let totalVal = 0, totalPL = 0, totalCost = 0;
      for (const p of sorted) {
        const w = p.walletImpact;
        const val = w?.currentValue ?? p.currentPrice * p.quantity;
        const pl = w?.unrealizedProfitLoss ?? 0;
        const cost = w?.totalCost ?? p.averagePricePaid * p.quantity;
        const pct = cost > 0 ? (pl / cost) * 100 : 0;
        const ccy = w?.currency ?? p.instrument.currency;
        totalVal += val;
        totalPL += pl;
        totalCost += cost;
        const sign = pl >= 0 ? "+" : "";
        console.log(`${p.instrument.ticker.padEnd(16)} ${p.instrument.name.padEnd(30).slice(0,30)} ${p.quantity.toFixed(2).padStart(10)} @ ${p.averagePricePaid.toFixed(2).padStart(8)} → ${p.currentPrice.toFixed(2).padStart(8)}  |  ${val.toFixed(2).padStart(10)} ${ccy}  |  ${sign}${pl.toFixed(2)} (${sign}${pct.toFixed(1)}%)`);
      }
      console.log(`\nPositions: ${positions.length} | Total: ${totalVal.toFixed(2)} | P/L: ${totalPL >= 0 ? "+" : ""}${totalPL.toFixed(2)}`);
      break;
    }
    case "position": {
      const positions = await client.getPositions(args[1]);
      console.log(JSON.stringify(positions, null, 2));
      break;
    }
    case "orders": {
      const orders = await client.getPendingOrders();
      if (!orders.length) { console.log("No pending orders."); break; }
      console.log(JSON.stringify(orders, null, 2));
      break;
    }
    case "order": {
      const order = await client.getOrderById(parseInt(args[1]));
      console.log(JSON.stringify(order, null, 2));
      break;
    }
    case "cancel": {
      await client.cancelOrder(parseInt(args[1]));
      console.log(`Order ${args[1]} cancelled.`);
      break;
    }
    case "buy-market": {
      const o = await client.placeMarketOrder({ ticker: args[1], quantity: parseFloat(args[2]) });
      console.log("Market buy order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "sell-market": {
      const o = await client.placeMarketOrder({ ticker: args[1], quantity: -Math.abs(parseFloat(args[2])) });
      console.log("Market sell order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "buy-limit": {
      const o = await client.placeLimitOrder({ ticker: args[1], quantity: parseFloat(args[2]), limitPrice: parseFloat(args[3]) });
      console.log("Limit buy order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "sell-limit": {
      const o = await client.placeLimitOrder({ ticker: args[1], quantity: -Math.abs(parseFloat(args[2])), limitPrice: parseFloat(args[3]) });
      console.log("Limit sell order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "buy-stop": {
      const o = await client.placeStopOrder({ ticker: args[1], quantity: parseFloat(args[2]), stopPrice: parseFloat(args[3]) });
      console.log("Stop buy order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "sell-stop": {
      const o = await client.placeStopOrder({ ticker: args[1], quantity: -Math.abs(parseFloat(args[2])), stopPrice: parseFloat(args[3]) });
      console.log("Stop sell order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "buy-stop-limit": {
      const o = await client.placeStopLimitOrder({ ticker: args[1], quantity: parseFloat(args[2]), stopPrice: parseFloat(args[3]), limitPrice: parseFloat(args[4]) });
      console.log("Stop-limit buy order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "sell-stop-limit": {
      const o = await client.placeStopLimitOrder({ ticker: args[1], quantity: -Math.abs(parseFloat(args[2])), stopPrice: parseFloat(args[3]), limitPrice: parseFloat(args[4]) });
      console.log("Stop-limit sell order placed:", JSON.stringify(o, null, 2));
      break;
    }
    case "history-orders": {
      const h = await client.getHistoricalOrders(20);
      console.log(JSON.stringify(h, null, 2));
      break;
    }
    case "dividends": {
      const d = await client.getDividends(20);
      console.log(JSON.stringify(d, null, 2));
      break;
    }
    case "transactions": {
      const t = await client.getTransactions(20);
      console.log(JSON.stringify(t, null, 2));
      break;
    }
    case "instruments": {
      const instruments = await client.getInstruments();
      console.log(`Total instruments: ${instruments.length}`);
      for (const i of instruments.slice(0, 20)) {
        console.log(`${i.ticker.padEnd(20)} ${i.name.padEnd(40)} ${i.type.padEnd(10)} ${i.currencyCode}`);
      }
      if (instruments.length > 20) console.log(`... and ${instruments.length - 20} more`);
      break;
    }
    case "exchanges": {
      const exchanges = await client.getExchanges();
      console.log(JSON.stringify(exchanges, null, 2));
      break;
    }
    case "reports": {
      const reports = await client.getReports();
      console.log(JSON.stringify(reports, null, 2));
      break;
    }
    default:
      console.error(`Unknown command: ${command}. Run with --help for usage.`);
      process.exit(1);
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
