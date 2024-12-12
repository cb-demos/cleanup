FROM alpine:3.21

RUN apk add --no-cache \
    python3 \
    helm \
    kubectl

WORKDIR /app

COPY . .
