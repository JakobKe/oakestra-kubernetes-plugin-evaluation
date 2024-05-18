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
	}

}

func consumeCPU() {
	fmt.Println("CPU-intensive Berechnung gestartet...")
	for i := 0; i < 10000000; i++ {
		math.Pow(2, 10)
	}
}
