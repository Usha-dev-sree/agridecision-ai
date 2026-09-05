# ── Agronomist Portal — Dockerfile ─────────────────────────────────────────
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy workspace root package files for turborepo
COPY package.json package-lock.json* turbo.json ./
COPY frontend/apps/agronomist-portal/package.json ./frontend/apps/agronomist-portal/

# Install all dependencies
RUN npm install --prefix frontend/apps/agronomist-portal

# Copy the full frontend source
COPY frontend/apps/agronomist-portal/ ./frontend/apps/agronomist-portal/

# Build the Vite production bundle
WORKDIR /app/frontend/apps/agronomist-portal
RUN npm run build

# ── Runtime: serve with nginx ────────────────────────────────────────────────
FROM nginx:stable-alpine

# Copy built assets
COPY --from=builder /app/frontend/apps/agronomist-portal/dist /usr/share/nginx/html

# Nginx config with API proxying and SPA fallback
RUN printf 'server {\n\
    listen 3000;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    location /api/auth/ {\n\
        proxy_pass http://agri-user-service:8000/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/farm/ {\n\
        proxy_pass http://agri-farm-service:8001/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/advisory/ {\n\
        proxy_pass http://agri-advisory-service:8002/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/weather/ {\n\
        proxy_pass http://agri-weather-service:8003/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/market/ {\n\
        proxy_pass http://agri-market-service:8004/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/analytics/ {\n\
        proxy_pass http://agri-analytics-service:8005/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/financial/ {\n\
        proxy_pass http://agri-financial-service:8006/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/notification/ {\n\
        proxy_pass http://agri-notification-service:8007/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/enterprise/ {\n\
        proxy_pass http://agri-enterprise-service:8008/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/iot/ {\n\
        proxy_pass http://agri-iot-service:8009/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
    location /api/ai/ {\n\
        proxy_pass http://agri-advisory-service:8002/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
    }\n\
\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    location /health {\n\
        return 200 "ok";\n\
        add_header Content-Type text/plain;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
