FROM golang:1.22 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o prediction-api main.go

FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /app/prediction-api .

EXPOSE 8080

CMD ["./prediction-api"]
