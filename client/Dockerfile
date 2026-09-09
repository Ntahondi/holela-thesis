# ==============================================================================
# Dockerfile for SMMS Cross-Platform Flutter Web Client
# Multi-stage build: Flutter SDK -> Lightweight Nginx Web Server
# ==============================================================================

# Stage 1: Build Flutter Web Bundle
FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app

# Copy dependency definition
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get

# Copy source code and build web release
COPY . .
RUN flutter build web --release

# Stage 2: Serve using Nginx
FROM nginx:alpine

# Copy built web assets to Nginx html directory
COPY --from=build /app/build/web /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
