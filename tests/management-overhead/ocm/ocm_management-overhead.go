package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"text/template"
	"time"
)

var (
	config Config
)

type PodInfo struct {
	Name            string
	ReadyToStart    string
	Initialized     string
	Ready           string
	ContainersReady string
	PodScheduled    string
}

type UndeploymentInfo struct {
	FinalizedTime time.Time
}

type DeploymentInfo struct {
	DeploymentTime   time.Time
	UndeploymentTime time.Time
	FinalizedTime    time.Time
	PodInfo          PodInfo
}

type Config struct {
	Duration int
	Replicas int
	VU       int
	ServerIP string
}

func generateYAML(config Config, templatePath string) (string, error) {
	tmpl, err := template.ParseFiles(templatePath)
	if err != nil {
		return "", fmt.Errorf("error parsing template file: %v", err)
	}

	var output bytes.Buffer
	if err := tmpl.Execute(&output, config); err != nil {
		return "", fmt.Errorf("error executing template: %v", err)
	}

	return output.String(), nil
}

func main() {

	tempFilePath := "./management-overhead.ocm.template.yaml"
	filePath := "./management-overhead.ocm.yaml"
	config = Config{
		Duration: 2700,
		Replicas: 10,
		VU:       10,
		ServerIP: "10.99.144.18",
	}

	content, _ := generateYAML(config, tempFilePath)
	err := os.WriteFile(filePath, []byte(content), 0644)
	if err != nil {
		fmt.Println("Error writing YAML to file:", err)
		return
	}
	fmt.Println("Start Deployment...")
	deployOCMLoadtest(filePath)

	// Wait 60 seconds for starting deployments and starting measurement
	time.Sleep(60 * time.Second)

	// Start Time for Test
	fmt.Print("Start Timer for Measurement...")
	START := time.Now()
	time.Sleep(time.Duration(config.Duration) * time.Second)

	// Undeploy Tests
	undeployOCMLoadtest(filePath)

	fmt.Println("Start Timestamp of Test:  ", START)
}

func deployOCMLoadtest(filePath string) error {
	context := "kubernetes-admin@kubernetes"
	cmd := exec.Command("kubectl", "--kubeconfig", "./ocm.config", "create", "-f", filePath, "--context", context)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
		fmt.Println(output)
		return err
	}

	return nil
}

func undeployOCMLoadtest(filePath string) error {
	context := "kubernetes-admin@kubernetes"
	cmd := exec.Command("kubectl", "--kubeconfig", "./ocm.config", "delete", "-f", filePath, "--context", context)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
		fmt.Println(output)
		return err
	}

	return nil
}
