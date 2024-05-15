FROM golang:1.22-alpine AS builder
WORKDIR /app

COPY . .

RUN go build -o client

FROM alpine:latest
WORKDIR /app

COPY --from=builder /app/client .

ENV NUM_PROGRAMS 10
ENV DURATION_IN_SECONDS 60
ENV SERVICE_URL "management-overhead.default.svc.cluster.local"

CMD ["./client"]
