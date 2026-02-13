import axios from 'axios';
import fs from 'fs';

const apiKey = fs.readFileSync('/home/lstopar/.openclaw/workspace/trading212_api_key.txt', 'utf-8').trim();

axios.get('https://live.trading212.com/api/v0/equity/account/cash', {
  headers: {
    'Authorization': apiKey,
    'Content-Type': 'application/json',
  },
})
.then(response => {
  console.log('Account Balance:', response.data);
})
.catch(error => {
  console.error('Error:', error.response?.data || error.message);
});