# Root Dockerfile — builds the Go metrics/API binary.
# Each service also has its own Dockerfile under services/ and frontend/.

FROM golang:1.22 AS builder

WORKDIR /app

COPY services/prediction-api-go/go.mod services/prediction-api-go/go.sum ./
RUN go mod download

COPY services/prediction-api-go/ .
RUN go build -o prediction-api main.go

FROM debian:bookworm-slim

WORKDIR /app
COPY --from=builder /app/prediction-api .

EXPOSE 8080

CMD ["./prediction-api"]
