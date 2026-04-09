# ── Build stage ──────────────────────────────────────────────
FROM node:20.20.2-alpine AS build

WORKDIR /app

# Install dependencies first (cache layer)
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# ── Production stage ─────────────────────────────────────────
FROM nginx:1.29.8-alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 4000

CMD ["nginx", "-g", "daemon off;"]
