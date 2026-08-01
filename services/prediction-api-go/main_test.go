package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
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

func TestPredictHandlerForwardsValidatedRequest(t *testing.T) {
	mockModel := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("expected POST, got %s", r.Method)
		}
		var input PredictRequest
		if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
			t.Fatalf("decode forwarded request: %v", err)
		}
		if len(input.Features) != expectedFeatureCount {
			t.Fatalf("expected %d features, got %d", expectedFeatureCount, len(input.Features))
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"prediction": 0.9, "model_version": "local-iris-binary-v1"}`))
	}))
	defer mockModel.Close()

	handler := makePredictHandler(mockModel.URL)
	req := httptest.NewRequest(http.MethodPost, "/predict", strings.NewReader(`{"features": [5.1, 3.5, 1.4, 0.2]}`))
	w := httptest.NewRecorder()

	handler(w, req)

	if w.Code != http.StatusOK {
		t.Fatalf("expected status 200, got %d", w.Code)
	}
	var result predictionResponse
	if err := json.NewDecoder(w.Body).Decode(&result); err != nil {
		t.Fatalf("response is not valid JSON: %v", err)
	}
	if result.Prediction != 0.9 || result.ModelVersion != "local-iris-binary-v1" {
		t.Fatalf("unexpected result: %+v", result)
	}
}

func TestPredictHandlerRejectsInvalidRequests(t *testing.T) {
	handler := makePredictHandler("http://127.0.0.1:1")
	tests := []struct {
		name   string
		method string
		body   string
		status int
	}{
		{name: "method", method: http.MethodGet, status: http.StatusMethodNotAllowed},
		{name: "malformed JSON", method: http.MethodPost, body: `{"features":`, status: http.StatusBadRequest},
		{name: "wrong feature count", method: http.MethodPost, body: `{"features": [1, 2, 3]}`, status: http.StatusBadRequest},
		{name: "unknown field", method: http.MethodPost, body: `{"features": [1, 2, 3, 4], "debug": true}`, status: http.StatusBadRequest},
		{name: "multiple JSON values", method: http.MethodPost, body: `{"features": [1, 2, 3, 4]} {}`, status: http.StatusBadRequest},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest(tt.method, "/predict", strings.NewReader(tt.body))
			w := httptest.NewRecorder()

			handler(w, req)

			if w.Code != tt.status {
				t.Fatalf("expected status %d, got %d", tt.status, w.Code)
			}
		})
	}
}

func TestPredictHandlerMapsInvalidUpstreamResponses(t *testing.T) {
	tests := []struct {
		name       string
		statusCode int
		body       string
	}{
		{name: "upstream error", statusCode: http.StatusInternalServerError, body: `{"detail":"internal"}`},
		{name: "malformed JSON", statusCode: http.StatusOK, body: `not json`},
		{name: "missing model version", statusCode: http.StatusOK, body: `{"prediction": 0.9}`},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mockModel := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
				w.WriteHeader(tt.statusCode)
				_, _ = w.Write([]byte(tt.body))
			}))
			defer mockModel.Close()

			handler := makePredictHandler(mockModel.URL)
			req := httptest.NewRequest(http.MethodPost, "/predict", strings.NewReader(`{"features": [1, 2, 3, 4]}`))
			w := httptest.NewRecorder()

			handler(w, req)

			if w.Code != http.StatusBadGateway {
				t.Fatalf("expected status 502, got %d", w.Code)
			}
			if strings.Contains(w.Body.String(), "internal") {
				t.Fatalf("upstream error leaked to caller: %q", w.Body.String())
			}
		})
	}
}

func TestPredictHandlerMapsTimeoutToServiceUnavailable(t *testing.T) {
	mockModel := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		time.Sleep(50 * time.Millisecond)
		_, _ = w.Write([]byte(`{"prediction": 0.9, "model_version": "late"}`))
	}))
	defer mockModel.Close()

	handler := makePredictHandlerWithClient(mockModel.URL, &http.Client{Timeout: 5 * time.Millisecond})
	req := httptest.NewRequest(http.MethodPost, "/predict", strings.NewReader(`{"features": [1, 2, 3, 4]}`))
	w := httptest.NewRecorder()

	handler(w, req)

	if w.Code != http.StatusServiceUnavailable {
		t.Fatalf("expected status 503, got %d", w.Code)
	}
}

