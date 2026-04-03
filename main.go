import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var requestCounter = prometheus.NewCounter(
	prometheus.CounterOpts{
		Name: "requests_total",
		Help: "Total number of requests",
	},
)
