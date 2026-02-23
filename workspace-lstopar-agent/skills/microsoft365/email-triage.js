// Email triage helper - fetches recent emails with full details
const { getAccessToken } = require('./src/auth');
const { normalizeAccount } = require('./src/config');

const GRAPH_BASE = 'https://graph.microsoft.com/v1.0';

async function callGraph(endpoint, method = 'GET', body = null) {
  const account = normalizeAccount('default');
  const token = await getAccessToken(account);
  if (!token) throw new Error('No access token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);
  const url = endpoint.startsWith('http') ? endpoint : `${GRAPH_BASE}${endpoint}`;
  const res = await fetch(url, options);
  if (!res.ok) { const t = await res.text(); throw new Error(`Graph ${res.status}: ${t}`); }
  if (res.status === 204 || res.status === 202) return null;
  return res.json();
}

async function main() {
  const cmd = process.argv[2];

  if (cmd === 'list') {
    // List emails since N hours ago
    const hoursAgo = parseInt(process.argv[3] || '6');
    const since = new Date(Date.now() - hoursAgo * 3600000).toISOString();
    const filter = `receivedDateTime ge ${since}`;
    const select = 'id,subject,from,receivedDateTime,isRead,bodyPreview,parentFolderId,webLink';
    const endpoint = `/me/messages?$filter=${encodeURIComponent(filter)}&$select=${select}&$orderby=receivedDateTime desc&$top=50`;
    const res = await callGraph(endpoint);
    console.log(JSON.stringify(res?.value || [], null, 2));
  }
  else if (cmd === 'get') {
    // Get full message
    const id = process.argv[3];
    const res = await callGraph(`/me/messages/${id}?$select=id,subject,from,toRecipients,ccRecipients,receivedDateTime,body,bodyPreview,webLink,parentFolderId`);
    console.log(JSON.stringify(res, null, 2));
  }
  else if (cmd === 'move') {
    // Move to folder
    const id = process.argv[3];
    const folder = process.argv[4] || 'archive';
    const res = await callGraph(`/me/messages/${id}/move`, 'POST', { destinationId: folder });
    console.log(JSON.stringify(res, null, 2));
  }
  else if (cmd === 'reply-draft') {
    // Create reply-all draft. Body text from stdin.
    const id = process.argv[3];
    const chunks = [];
    for await (const chunk of process.stdin) chunks.push(chunk);
    const bodyText = Buffer.concat(chunks).toString('utf8').trim();
    
    // Create reply all
    const draft = await callGraph(`/me/messages/${id}/createReplyAll`, 'POST', {
      comment: bodyText
    });
    // Get the draft to retrieve webLink
    if (draft?.id) {
      const full = await callGraph(`/me/messages/${draft.id}?$select=id,webLink`);
      console.log(JSON.stringify({ draftId: draft.id, link: full?.webLink }, null, 2));
    } else {
      console.log(JSON.stringify(draft, null, 2));
    }
  }
  else {
    console.log('Usage: node email-triage.js <list|get|move|reply-draft> [args]');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
