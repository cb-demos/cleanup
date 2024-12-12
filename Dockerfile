FROM alpine:3.21

RUN apk add --no-cache \
    python3 \
    helm \
    kubectl

RUN adduser -D cleaner

USER cleaner

WORKDIR /app

COPY . .
