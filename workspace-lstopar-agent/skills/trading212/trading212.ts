import axios from 'axios';
import fs from 'fs';

interface Trading212Auth {
  apiKey: string;
}

interface AccountBalance {
  total: number;          // Total balance
  available: number;      // Available funds
  invested: number;       // Invested amount
  ppl: number;            // Profit/loss
  result: number;         // Result (total + ppl)
}

export class Trading212Client {
  private client: axios.AxiosInstance;

  constructor(auth: Trading212Auth) {
    this.client = axios.create({
      baseURL: 'https://live.trading212.com/api/v0',
      headers: {
        'Authorization': auth.apiKey,
        'Content-Type': 'application/json',
      },
    });
  }

  async getAccountBalance(): Promise<AccountBalance> {
    const response = await this.client.get('/equity/account/cash');
    return response.data;
  }
}

// Fetch balance using the API key from file
export async function fetchBalance(): Promise<AccountBalance> {
  const apiKey = fs.readFileSync('/home/lstopar/.openclaw/workspace/trading212_api_key.txt', 'utf-8').trim();
  const client = new Trading212Client({ apiKey });
  return await client.getAccountBalance();
}