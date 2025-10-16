# ---------- BUILD STAGE ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy package metadata first (better caching)
COPY package*.json ./

# Install dependencies (using ci for clean reproducible builds)
RUN npm ci

# Copy app source
COPY . .

# Environment tweaks to avoid memory and telemetry issues
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_OPTIONS="--max-old-space-size=2048"

# Build and export static Next.js site
RUN npm run build || (cat /root/.npm/_logs/* && false)
RUN npm run export || (cat /root/.npm/_logs/* && false)

# ---------- RUNTIME STAGE ----------
FROM nginx:1.27-alpine
WORKDIR /usr/share/nginx/html

# Clean default files and copy build output
RUN rm -rf ./*
COPY --from=builder /app/out .

# Minimal nginx config
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

