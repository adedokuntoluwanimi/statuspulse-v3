# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Only copy package metadata first (for caching)
COPY package*.json ./
RUN npm ci --omit=dev

# Copy source and build static export
COPY . .
RUN npm run build && npm run export

# ---------- RUNTIME STAGE ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# Clean default files and copy build output
RUN rm -rf ./*
COPY --from=builder /app/out .

# Minimal nginx config: serve static + proxy /api to backend
RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
\n\
    location /api/ {\n\
        proxy_pass http://backend:8000/;\n\
    }\n\
\n\
    location / {\n\
        try_files $uri /index.html;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
