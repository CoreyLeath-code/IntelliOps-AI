package main

import (
	"log"
	"net/http"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var requestCounter = prometheus.NewCounter(
	prometheus.CounterOpts{
		Name: "requests_total",
		Help: "Total number of requests",
	},
)

func init() {
	prometheus.MustRegister(requestCounter)
}

func main() {
	http.Handle("/metrics", promhttp.Handler())
	log.Println("Metrics server listening on :2112")
	log.Fatal(http.ListenAndServe(":2112", nil))
}
