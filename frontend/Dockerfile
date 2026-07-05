FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./

RUN npm install -g pnpm

RUN pnpm install

COPY . .

RUN pnpm build

FROM node:20-alpine AS runner

WORKDIR /app

RUN addgroup -g 1001 synapsehr && adduser -u 1001 -G synapsehr -s /bin/sh -D synapsehr

COPY --from=builder /app/dist ./dist

USER synapsehr

EXPOSE 4321

CMD ["node", "dist/server/entry.mjs"]
