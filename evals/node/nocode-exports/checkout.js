'use strict';

function calculateRisk(order) { return order.channel === 'web' ? 1 : 2; }

async function submit(order) {
  if (!order) throw new Error('order required');
  return { risk: calculateRisk(order) };
}

module.exports = { submit };
