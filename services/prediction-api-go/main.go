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

type Request struct {
	Features []float64 `json:"features"`
}

func main() {
	modelURL := os.Getenv("MODEL_SERVICE_URL")
	if modelURL == "" {
		modelURL = "http://ml-model:8001/predict"
	}

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok"))
	})

	http.HandleFunc("/predict", func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		requestCounter.Inc()

		var req Request
		json.NewDecoder(r.Body).Decode(&req)

		payload, _ := json.Marshal(req)

		resp, err := http.Post(modelURL, "application/json", bytes.NewBuffer(payload))
		if err != nil {
			http.Error(w, "model service unavailable", 500)
			return
		}
		defer resp.Body.Close()

		var result map[string]interface{}
		json.NewDecoder(resp.Body).Decode(&result)

		latency := time.Since(start).Milliseconds()
		log.Printf("latency=%dms", latency)

		json.NewEncoder(w).Encode(result)
	})

	http.Handle("/metrics", promhttp.Handler())

	log.Println("API listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
