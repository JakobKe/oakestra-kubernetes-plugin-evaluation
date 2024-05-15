package main

import (
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM)

	go func() {
		// ReadinessProbe for Kubernetes Pod
		http.HandleFunc("/ready", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(200)
			w.Write([]byte("ok"))
		})
		if err := http.ListenAndServe(":7070", nil); err != nil {
			fmt.Println("Error starting HTTP server:", err)
			os.Exit(1)
		}
	}()

	fmt.Println("Awaiting SIGTERM to exit")
	sig := <-sigs
	fmt.Println("Received signal:", sig)

	fmt.Println("Exiting program.")
	os.Exit(0)
}
