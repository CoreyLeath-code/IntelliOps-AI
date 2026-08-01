package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

const (
	expectedFeatureCount = 4
	maxRequestBodyBytes  = 1 << 20
	modelRequestTimeout  = 5 * time.Second
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

// predictionResponse is the validated payload returned by the model service.
type predictionResponse struct {
	Prediction   float64 `json:"prediction"`
	ModelVersion string  `json:"model_version"`
}

// healthHandler responds with a simple "ok" status.
func healthHandler(w http.ResponseWriter, _ *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ok"))
}

// makePredictHandler returns an http.HandlerFunc that proxies prediction
// requests to the downstream model service at modelURL.
func makePredictHandler(modelURL string) http.HandlerFunc {
	return makePredictHandlerWithClient(modelURL, &http.Client{Timeout: modelRequestTimeout})
}

func makePredictHandlerWithClient(modelURL string, client *http.Client) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		requestCounter.Inc()
		defer func() {
			log.Printf("latency=%dms", time.Since(start).Milliseconds())
		}()

		if r.Method != http.MethodPost {
			w.Header().Set("Allow", http.MethodPost)
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}

		defer r.Body.Close()
		decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, maxRequestBodyBytes))
		decoder.DisallowUnknownFields()

		var req PredictRequest
		if err := decoder.Decode(&req); err != nil {
			http.Error(w, "invalid request body", http.StatusBadRequest)
			return
		}
		if err := decoder.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
			http.Error(w, "invalid request body", http.StatusBadRequest)
			return
		}
		if !validFeatures(req.Features) {
			http.Error(w, "features must contain exactly four finite values", http.StatusBadRequest)
			return
		}

		payload, err := json.Marshal(req)
		if err != nil {
			log.Printf("prediction request serialization failed: %v", err)
			http.Error(w, "invalid request body", http.StatusBadRequest)
			return
		}

		upstreamRequest, err := http.NewRequestWithContext(r.Context(), http.MethodPost, modelURL, bytes.NewReader(payload))
		if err != nil {
			log.Printf("model request construction failed: %v", err)
			http.Error(w, "model service unavailable", http.StatusServiceUnavailable)
			return
		}
		upstreamRequest.Header.Set("Content-Type", "application/json")

		resp, err := client.Do(upstreamRequest)
		if err != nil {
			log.Printf("model request failed: %v", err)
			http.Error(w, "model service unavailable", http.StatusServiceUnavailable)
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
			log.Printf("model service returned status=%d", resp.StatusCode)
			http.Error(w, "model service returned an invalid response", http.StatusBadGateway)
			return
		}

		var result predictionResponse
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil || !validPrediction(result) {
			if err != nil {
				log.Printf("model response decoding failed: %v", err)
			} else {
				log.Printf("model response failed contract validation")
			}
			http.Error(w, "model service returned an invalid response", http.StatusBadGateway)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(result); err != nil {
			log.Printf("prediction response encoding failed: %v", err)
		}
	}
}

func validFeatures(features []float64) bool {
	if len(features) != expectedFeatureCount {
		return false
	}
	for _, feature := range features {
		if math.IsNaN(feature) || math.IsInf(feature, 0) {
			return false
		}
	}
	return true
}

func validPrediction(result predictionResponse) bool {
	return result.ModelVersion != "" && result.Prediction >= 0 && result.Prediction <= 1 && !math.IsNaN(result.Prediction) && !math.IsInf(result.Prediction, 0)
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
