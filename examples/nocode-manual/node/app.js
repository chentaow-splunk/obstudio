'use strict';

const checkout = require('./checkout');

(async () => {
  const results = [];
  for (const channel of ['web', null, 'throw']) {
    try { results.push(await checkout.submit(channel)); }
    catch { results.push('error'); }
  }
  console.log('LAB_RESULT ' + JSON.stringify({ results, excluded: checkout.excluded() }));
  // Keep this short-lived sample alive for the agent's unref'ed batch exporter.
  await new Promise(resolve => setTimeout(resolve, 1000));
})().catch(error => { console.error(error); process.exitCode = 1; });
