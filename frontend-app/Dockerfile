# === STAGE 1: Build React App ===
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source và build
COPY . .
RUN npm run build

# === STAGE 2: Nginx Production Server ===
FROM nginx:alpine

# Copy built artifacts từ stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy Nginx config (xử lý proxy /api và SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Railway inject PORT và BACKEND_URL vào environment.
# envsubst thay thế cả 2 biến ${PORT} và ${BACKEND_URL} trong nginx.conf
CMD envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp && \
    mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf && \
    nginx -g 'daemon off;'
