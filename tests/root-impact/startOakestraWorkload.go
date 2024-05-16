package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"time"
)

var (
	SYSTEM_MANAGER_URL   = "10.100.253.175:10000"
	CLIENT_SERVICE_ID    = ""
	DEPLOYMENT_BASE_NAME = ""
)

type Application struct {
	ApplicationID string   `json:"applicationID"`
	Microservices []string `json:"microservices"`
}

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

func main() {

	numberOfServices := 5
	SLA_FILE := "./root-impact_SD.json"

	deleteAllApps()

	DEPLOYMENT_BASE_NAME, _ = getDeploymentBaseName(SLA_FILE)
	deyploymentDescriptor := loadSLAFile(SLA_FILE)

	appID, services, _ := registerApp(deyploymentDescriptor)

	if appID == "" {
		fmt.Println("App registration failed")
		fmt.Println("Forcing undeployment. Please wait for the cleanup to finish")

		undeployAll(appID)

		time.Sleep(20 * time.Second)

		fmt.Println("You may now fix your infrastructure and re-try the test")
		os.Exit(1)
	}

	CLIENT_SERVICE_ID = services[0]
	deployOakestra(numberOfServices)

	CLIENT_SERVICE_ID = services[1]
	deployOakestra(numberOfServices)

	fmt.Println("Oakestra deployed, now waiting 5 Minutes to gather data.")
	time.Sleep(6 * time.Minute)

	deleteAllApps()
}

func getDeploymentBaseName(filename string) (string, error) {

	type Microservice struct {
		MicroserviceName      string `json:"microservice_name"`
		MicroserviceNamespace string `json:"microservice_namespace"`
	}
	type Application struct {
		ApplicationName      string         `json:"application_name"`
		ApplicationNamespace string         `json:"application_namespace"`
		Microservices        []Microservice `json:"microservices"`
	}

	type SLAFile struct {
		Applications []Application `json:"applications"`
	}

	var slaFile SLAFile

	jsonFile, err := os.Open(filename)
	if err != nil {
		return "slaFile", fmt.Errorf("error opening SLA file: %v", err)
	}
	defer jsonFile.Close()

	if err := json.NewDecoder(jsonFile).Decode(&slaFile); err != nil {
		return "slaFile", fmt.Errorf("error decoding JSON: %v", err)
	}

	app := slaFile.Applications[0]
	appName := app.ApplicationName
	appNamespace := app.ApplicationNamespace

	ms := app.Microservices[0]
	serviceName := ms.MicroserviceName
	serviceNamespace := ms.MicroserviceNamespace

	deploymentBaseName := fmt.Sprintf("%s.%s.%s.%s.", appName, appNamespace, serviceName, serviceNamespace)

	return deploymentBaseName, nil
}

func getLogin() (string, error) {
	url := "http://" + SYSTEM_MANAGER_URL + "/api/auth/login"
	credentials := map[string]string{
		"username": "Admin",
		"password": "Admin",
	}
	jsonData, err := json.Marshal(credentials)
	if err != nil {
		return "", fmt.Errorf("failed to marshal JSON: %v", err)
	}

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("failed to send POST request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("received unexpected status code: %d", resp.StatusCode)
	}

	type LoginResponse struct {
		RefreshToken string `json:"refresh_token"`
		Token        string `json:"token"`
	}

	var loginResponse LoginResponse
	if err := json.NewDecoder(resp.Body).Decode(&loginResponse); err != nil {
		return "", fmt.Errorf("failed to decode response JSON: %v", err)
	}

	return loginResponse.Token, nil
}

func loadSLAFile(SLA_FILE string) map[string]interface{} {

	var deploymentDescriptor map[string]interface{}

	// Open the SLA file
	jsonFile, err := os.Open(SLA_FILE)
	if err != nil {
		fmt.Printf("Error opening SLA file: %v\n", err)
		return nil
	}
	defer jsonFile.Close()

	// Decode the JSON file into deployment descriptor
	if err := json.NewDecoder(jsonFile).Decode(&deploymentDescriptor); err != nil {
		fmt.Printf("Error decoding JSON: %v\n", err)
		return nil
	}

	return deploymentDescriptor
}

func registerApp(deployment_descriptor map[string]interface{}) (string, []string, error) {
	token, _ := getLogin()

	head := map[string]string{
		"Authorization": "Bearer " + token,
	}

	jsonData, err := json.Marshal(deployment_descriptor)
	if err != nil {
		return "", nil, fmt.Errorf("failed to marshal JSON: %v", err)
	}

	url := "http://" + SYSTEM_MANAGER_URL + "/api/application"
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", nil, fmt.Errorf("failed to create request: %v", err)
	}
	for key, value := range head {
		req.Header.Set(key, value)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := ioutil.ReadAll(resp.Body)
		fmt.Println(string(body))
		return "", nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	body, _ := ioutil.ReadAll(resp.Body)

	var s string
	if err := json.Unmarshal(body, &s); err != nil {
		panic(err)
	}

	var applications []Application
	err = json.Unmarshal([]byte(s), &applications)
	if err != nil {
		fmt.Println("Error unmarshalling JSON:", err)

	}

	return applications[0].ApplicationID, applications[0].Microservices, nil
}

func deployOakestra(numberOfServices int) map[string]DeploymentInfo {
	token, _ := getLogin()
	deploymentInfos := make(map[string]DeploymentInfo)

	url := fmt.Sprintf("http://%s/api/service/%s/instance", SYSTEM_MANAGER_URL, CLIENT_SERVICE_ID)

	for i := 0; i < numberOfServices; i++ {

		client := &http.Client{}
		req, err := http.NewRequest("POST", url, bytes.NewBuffer(nil))
		if err != nil {
			fmt.Printf("Failed to create request: %v\n", err)
			os.Exit(1)
		}
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))

		resp, err := client.Do(req)
		if err != nil {
			fmt.Printf("Failed to send request: %v\n", err)
			os.Exit(1)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Deploy request failed!!\n")
			fmt.Printf("Response: %v\n", resp)
			os.Exit(1)
		}
		deploymentInfos[DEPLOYMENT_BASE_NAME+strconv.Itoa(i)] = DeploymentInfo{DeploymentTime: time.Now()}
	}

	return deploymentInfos
}

func undeployAll(appID string) {
	fmt.Println("\t Asking Undeployment")
	token, _ := getLogin()
	url := fmt.Sprintf("http://%s/api/application/%s", SYSTEM_MANAGER_URL, appID)
	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		fmt.Println("Error creating HTTP request:", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+token)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending HTTP request:", err)
		return
	}
	defer resp.Body.Close()
	time.Sleep(10 * time.Second)
}

func deleteAllApps() {
	token, _ := getLogin()
	url := fmt.Sprintf("http://%s/api/services", SYSTEM_MANAGER_URL)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println("Error creating HTTP request:", err)
		return
	}
	req.Header.Set("Authorization", "Bearer "+token)
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending HTTP request:", err)
		return
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusOK {
		body, _ := ioutil.ReadAll(resp.Body)
		// fmt.Println(string(body))

		var s string
		if err := json.Unmarshal(body, &s); err != nil {
			panic(err)
		}

		var applications []Application
		err = json.Unmarshal([]byte(s), &applications)
		if err != nil {
			fmt.Println("Error unmarshalling JSON:", err)

		}
		for _, application := range applications {
			appID := application.ApplicationID
			url := fmt.Sprintf("http://%s/api/application/%s", SYSTEM_MANAGER_URL, appID)
			req, err := http.NewRequest("DELETE", url, nil)
			if err != nil {
				fmt.Println("Error creating HTTP request:", err)
				return
			}
			req.Header.Set("Authorization", "Bearer "+token)
			resp, err := client.Do(req)
			if err != nil {
				fmt.Println("Error sending HTTP request:", err)
				continue
			}
			resp.Body.Close()
		}

		fmt.Println("All Apps Deleted")
		return
	}
}
