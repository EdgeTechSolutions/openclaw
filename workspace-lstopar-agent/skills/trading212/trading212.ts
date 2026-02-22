import axios from 'axios';
import fs from 'fs';

interface Trading212Auth {
  apiKeyId: string;
  secretKey: string;
}

interface AccountBalance {
  total: number;
  available: number;
  invested: number;
  ppl: number;
  result: number;
  free: number;
  pieCash: number;
  blocked: number;
}

export class Trading212Client {
  private client: axios.AxiosInstance;

  constructor(auth: Trading212Auth) {
    this.client = axios.create({
      baseURL: 'https://live.trading212.com/api/v0',
      auth: {
        username: auth.apiKeyId,
        password: auth.secretKey,
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getAccountBalance(): Promise<AccountBalance> {
    const response = await this.client.get('/equity/account/cash');
    return response.data;
  }
}

export function loadConfig(path = '/workspace/.trading212-config.json'): Trading212Auth {
  const config = JSON.parse(fs.readFileSync(path, 'utf-8'));
  return { apiKeyId: config.apiKeyId, secretKey: config.secretKey };
}

export async function fetchBalance(): Promise<AccountBalance> {
  const auth = loadConfig();
  const client = new Trading212Client(auth);
  return await client.getAccountBalance();
}
