package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHealthEndpoint(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()

	healthHandler(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("expected status 200, got %d", w.Code)
	}
	if w.Body.String() != "ok" {
		t.Errorf("expected body 'ok', got %q", w.Body.String())
	}
}

func TestPredictHandlerForwardsToModel(t *testing.T) {
	// Start a mock model service that returns a canned prediction.
	mockModel := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"prediction": 0.9, "model_version": "local-iris-binary-v1"}`))
	}))
	defer mockModel.Close()

	handler := makePredictHandler(mockModel.URL)

	body := strings.NewReader(`{"features": [5.1, 3.5, 1.4, 0.2]}`)
	req := httptest.NewRequest(http.MethodPost, "/predict", body)
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	handler(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("expected status 200, got %d", w.Code)
	}

	var result map[string]interface{}
	if err := json.NewDecoder(w.Body).Decode(&result); err != nil {
		t.Fatalf("response is not valid JSON: %v", err)
	}
	if _, ok := result["prediction"]; !ok {
		t.Errorf("response missing 'prediction' field: %v", result)
	}
}

func TestPredictHandlerModelUnavailable(t *testing.T) {
	// Point to a server that immediately closes connections.
	handler := makePredictHandler("http://127.0.0.1:1") // no server on port 1

	body := strings.NewReader(`{"features": [1, 2, 3, 4]}`)
	req := httptest.NewRequest(http.MethodPost, "/predict", body)
	w := httptest.NewRecorder()

	handler(w, req)

	if w.Code != http.StatusServiceUnavailable {
		t.Errorf("expected 503, got %d", w.Code)
	}
}
