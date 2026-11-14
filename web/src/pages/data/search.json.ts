// Small search file for the browser: the alias map and the MiniSearch documents.
// Built from muni.json so the search page doesn't load the whole file.
import { data } from '../../lib/data';

export function GET() {
  const body = {
    checked_on: data.checked_on,
    alias: data.alias,
    docs: data.search_docs,
  };
  return new Response(JSON.stringify(body), { headers: { 'Content-Type': 'application/json' } });
}
