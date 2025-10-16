# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy only dependency metadata first for caching
COPY package*.json ./
RUN npm ci --omit=dev

# Copy rest of the project and build
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_OPTIONS="--max-old-space-size=2048"
RUN npm run build

# ---------- RUNTIME STAGE ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# Clean default files
RUN rm -rf ./*

# Copy build output
COPY --from=builder /app/.next/static ./_next/static
COPY --from=builder /app/.next/server ./server
COPY --from=builder /app/public ./public

# Minimal nginx configuration
RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
\n\
    location /api/ {\n\
        proxy_pass http://backend:8081/;\n\
    }\n\
\n\
    location / {\n\
        root /usr/share/nginx/html/server/app;\n\
        try_files $uri /index.html;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

