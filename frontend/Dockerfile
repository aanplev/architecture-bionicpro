# ===== Build stage =====
FROM node:16-alpine AS build

WORKDIR /app

# --- build-time env ---
ARG REACT_APP_API_URL
ARG REACT_APP_KEYCLOAK_URL
ARG REACT_APP_KEYCLOAK_REALM
ARG REACT_APP_KEYCLOAK_CLIENT_ID

# --- expose env to react build ---
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_KEYCLOAK_URL=${REACT_APP_KEYCLOAK_URL}
ENV REACT_APP_KEYCLOAK_REALM=${REACT_APP_KEYCLOAK_REALM}
ENV REACT_APP_KEYCLOAK_CLIENT_ID=${REACT_APP_KEYCLOAK_CLIENT_ID}

# Copy package files
COPY package.json package-lock.json ./

# Install deps
RUN npm ci

# Copy source
COPY . .

# Build react
RUN npm run build

# ===== Runtime stage =====
FROM nginx:alpine

# Copy build artifacts
COPY --from=build /app/build /usr/share/nginx/html

# Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
