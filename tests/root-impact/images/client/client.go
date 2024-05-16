package main

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

var (
	numPrograms       int    = 10
	durationInSeconds int    = 60
	serviceURL        string = "10.30.55.55"
)

func loadEnvVariables() error {
	var err error
	numProgramsStr := os.Getenv("NUM_PROGRAMS")
	numPrograms, err = strconv.Atoi(numProgramsStr)
	if err != nil {
		fmt.Println("WARNING: reading the environment variable NUM_PROGRAMS. Take default: 10", err)
	}

	durationInSecondsStr := os.Getenv("DURATION_IN_SECONDS")
	durationInSeconds, err = strconv.Atoi(durationInSecondsStr)
	if err != nil {
		fmt.Println("WARNING: reading the environment variable DURATION_IN_SECONDS. Take default: 60", err)
	}

	serviceURL = os.Getenv("SERVICE_URL")
	if serviceURL == "" {
		fmt.Println("WARNING: reading the environment variable SERVICE_URL. Take default: 10.30.55.55", err)
	}

	fmt.Println(numPrograms, durationInSeconds, serviceURL)
	return nil
}

func main() {

	err := loadEnvVariables()
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("Env Variables loaded, waiting for Server to start")
	time.Sleep(20 * time.Second)
	var wg sync.WaitGroup

	for i := 0; i < numPrograms; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			runLoadTest()
		}()
	}

	wg.Wait()

	fmt.Println("Loadtest finished.")
}

func runLoadTest() {
	duration := time.Duration(durationInSeconds) * time.Second

	start := time.Now()

	url := "http://" + serviceURL + ":7070/generate-load"
	for time.Since(start) < duration {
		_, err := http.Get(url)
		if err != nil {
			fmt.Println("Fehler beim Senden der HTTP-Anfrage:", err)
		}

		// Warte eine Sekunde, um die Last zu verteilen
		time.Sleep(3 * time.Second)
	}

}
