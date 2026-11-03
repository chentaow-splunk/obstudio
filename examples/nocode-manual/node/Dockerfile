FROM node:22-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY app.js checkout.js ./
CMD ["node", "--require", "@splunk/otel/instrument", "app.js"]
