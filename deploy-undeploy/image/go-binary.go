package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
)

func main() {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM)

	fmt.Println("Awaiting SIGTERM to exit")
	sig := <-sigs
	fmt.Println("Received signal:", sig)

	fmt.Println("Exiting program.")
	os.Exit(0)
}
