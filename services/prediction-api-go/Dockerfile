FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o api main.go

FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/api .
EXPOSE 8080
CMD ["./api"]
