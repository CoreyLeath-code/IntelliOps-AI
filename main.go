package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Request struct {
	Features []float64 `json:"features"`
}

func main() {
	r := gin.Default()

	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "Go Prediction API Running"})
	})

	r.POST("/predict", func(c *gin.Context) {
		var req Request

		if err := c.BindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		payload, _ := json.Marshal(req)

		resp, err := http.Post(
			"http://localhost:8001/predict",
			"application/json",
			bytes.NewBuffer(payload),
		)

		if err != nil {
			c.JSON(500, gin.H{"error": "ML service unavailable"})
			return
		}

		defer resp.Body.Close()

		body, _ := ioutil.ReadAll(resp.Body)

		var result map[string]interface{}
		json.Unmarshal(body, &result)

		c.JSON(200, gin.H{
			"prediction": result["prediction"],
		})
	})

	r.Run(":8080")
}
