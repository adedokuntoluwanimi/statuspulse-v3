# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package metadata first for caching
COPY package*.json ./
RUN npm ci --omit=dev

# Copy the rest and build
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_OPTIONS="--max-old-space-size=2048"
RUN npm run build

# ---------- RUNTIME STAGE ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

RUN rm -rf ./*
COPY --from=builder /app/out .

RUN printf 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
\n\
    location /api/ {\n\
        proxy_pass http://backend:8081/;\n\
    }\n\
\n\
    location / {\n\
        try_files $uri /index.html;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

