package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var requestCounter = prometheus.NewCounter(prometheus.CounterOpts{
	Name: "requests_total",
	Help: "Total number of requests",
})

func init() {
	prometheus.MustRegister(requestCounter)
}

// PredictRequest is the JSON body expected by /predict.
type PredictRequest struct {
	Features []float64 `json:"features"`
}

// healthHandler responds with a simple "ok" status.
func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ok"))
}

// makePredictHandler returns an http.HandlerFunc that proxies prediction
// requests to the downstream model service at modelURL.
func makePredictHandler(modelURL string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		requestCounter.Inc()

		var req PredictRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, "invalid request body", http.StatusBadRequest)
			return
		}

		payload, _ := json.Marshal(req)

		resp, err := http.Post(modelURL, "application/json", bytes.NewBuffer(payload))
		if err != nil {
			http.Error(w, "model service unavailable", http.StatusServiceUnavailable)
			return
		}
		defer resp.Body.Close()

		var result map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&result)

		latency := time.Since(start).Milliseconds()
		log.Printf("latency=%dms", latency)

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	}
}

func main() {
	modelURL := os.Getenv("MODEL_SERVICE_URL")
	if modelURL == "" {
		modelURL = "http://ml-model:8001/predict"
	}

	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/predict", makePredictHandler(modelURL))
	http.Handle("/metrics", promhttp.Handler())

	log.Println("API listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
