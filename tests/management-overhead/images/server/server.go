package main

import (
	"fmt"
	"math"
	"net/http"
	"os"
)

func main() {

	// ReadinessProbe for Kubernetes Pod
	http.HandleFunc("/generate-load", func(w http.ResponseWriter, r *http.Request) {
		consumeCPU()
		w.WriteHeader(200)
		w.Write([]byte("ok"))
	})
	if err := http.ListenAndServe(":7070", nil); err != nil {
		fmt.Println("Error starting HTTP server:", err)
		os.Exit(1)
	} else {
		fmt.Println("HTTP server is running on port 7070")
	}

}

func consumeCPU() {
	fmt.Println("CPU-intensive Berechnung gestartet...")
	for i := 0; i < 50000000; i++ {
		math.Pow(2, 10)
	}
}
