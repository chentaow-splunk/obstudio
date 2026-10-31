'use strict';

async function submit(channel) {
  await new Promise(resolve => setTimeout(resolve, 80));
  if (channel === 'throw') throw new Error('sample failure');
  return channel == null ? 'unknown' : channel;
}

function internalHelper(value) { return value; }

module.exports = { submit, excluded: () => internalHelper(42) };
