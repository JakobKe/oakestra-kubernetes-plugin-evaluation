package main

import (
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

var (
	clientset            *kubernetes.Clientset
	SYSTEM_MANAGER_URL   = "10.100.253.57:10000"
	CLIENT_SERVICE_ID    = ""
	DEPLOYMENT_BASE_NAME = ""
	APP_NAME             = ""
)

type Application struct {
	ApplicationID string   `json:"applicationID"`
	Microservices []string `json:"microservices"`
}

type PodInfo struct {
	Name                      string
	ReadyToStart              string
	Initialized               string
	Ready                     string
	ContainersReady           string
	PodScheduled              string
	PodReadyToStartContainers string
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
	createK8SClient()
	fmt.Println("Start Test Deploy-Undeploy Oakestra")

	numberOfServices := 100
	SLA_FILE := "./deploy-undeploy-scheduler.json"

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
	deploymentInfos := deployOakestra(numberOfServices)

	//fmt.Println(deploymentInfos)
	// // Wait
	// // Oakestra needs some time
	fmt.Println("Oakestra is deploying")
	time.Sleep(15 * time.Second)

	deploymentInfos = getDeploymentInfoOakestra(deploymentInfos, "oakestra")

	copy := make(map[string]int)
	for key := range deploymentInfos {
		copy[key] = 0
	}

	cleanedPodsChan := make(chan map[string]time.Time)
	deletedDeploymentsChan := make(chan map[string]time.Time)
	errChan := make(chan error)

	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		fmt.Println("Routine get Informations starts...")
		cleanedPods, err := getFinalizedDeployments(copy)
		if err != nil {
			errChan <- err
			return
		}

		cleanedPodsChan <- cleanedPods
	}()

	go func() {
		defer wg.Done()
		fmt.Println("Routine Undeploy starts...")
		deletedDeployments := undeployOakestra(numberOfServices)

		deletedDeploymentsChan <- deletedDeployments
	}()

	go func() {
		wg.Wait()
		close(cleanedPodsChan)
		close(deletedDeploymentsChan)
		close(errChan)
	}()

	cleanedPods := <-cleanedPodsChan
	deletedDeployments := <-deletedDeploymentsChan
	err := <-errChan
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Println("Write to CSV")
	writeInfoToCSV("oakestra.deploy.undeploy.csv", deploymentInfos, deletedDeployments, cleanedPods)
}

func createK8SClient() {
	home := homedir.HomeDir()
	kubeconfig := home + "/.kube/config"

	config, err := clientcmd.BuildConfigFromFlags("", kubeconfig)
	if err != nil {
		log.Fatal(err)
	}

	clientset, err = kubernetes.NewForConfig(config)
	if err != nil {
		log.Fatal(err)
	}
}

func getFinalizedDeployments(deletedDeployments map[string]int) (map[string]time.Time, error) {
	cleanedPods := map[string]time.Time{}

	for {
		pods, err := clientset.CoreV1().Pods("oakestra").List(context.TODO(), metav1.ListOptions{
			LabelSelector: fmt.Sprintf("applicationName=%s", APP_NAME),
		})
		if err != nil {
			log.Printf("Error getting pods for finalized Information: %v\n", err)
			return nil, err
		}
		stillActiveDeployments := make(map[string]int, len(pods.Items))
		for _, pod := range pods.Items {
			if deploymentName, ok := pod.Labels["app"]; ok {
				stillActiveDeployments[deploymentName] = 0
			}
		}

		for deploymentName := range deletedDeployments {
			_, exists := stillActiveDeployments[deploymentName]
			if !exists {
				cleanedPods[deploymentName] = time.Now()
				delete(deletedDeployments, deploymentName)
			}
		}

		if len(pods.Items) == 0 {
			fmt.Println("No more pods left, stop loop")
			break
		}
	}

	return cleanedPods, nil
}

func writeInfoToCSV(csvName string, deploymentInfos map[string]DeploymentInfo, deletedDeployments map[string]time.Time, cleanedPods map[string]time.Time) {
	file, err := os.Create(csvName)
	if err != nil {
		log.Fatal("Cannot create file", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"DeploymentName", "PodName", "DeploymentTime", "PodScheduled", "Initialized", "PodReadyToStartContainers", "ContainersReady", "Ready", "DeleteTime", "CleanUpTime"})

	var cleanUpTime time.Time

	for key, deploymentInfo := range deploymentInfos {
		if deletedTime, exists := deletedDeployments[key]; exists {

			// If some values did not get saved.
			if cleanUpTime, exists = cleanedPods[key]; !exists {
				cleanUpTime = deletedTime
			}
			err := writer.Write([]string{
				key,
				deploymentInfo.PodInfo.Name,
				deploymentInfo.DeploymentTime.Format(time.RFC3339),
				deploymentInfo.PodInfo.PodScheduled,
				deploymentInfo.PodInfo.Initialized,
				deploymentInfo.PodInfo.PodReadyToStartContainers,
				deploymentInfo.PodInfo.ContainersReady,
				deploymentInfo.PodInfo.Ready,
				deletedTime.Format(time.RFC3339),
				cleanUpTime.Format(time.RFC3339),
			})

			if err != nil {
				log.Fatal("Cannot write to file", err)
			}
		}
	}
}

func getDeploymentInfoOakestra(deploymentInfos map[string]DeploymentInfo, namespace string) map[string]DeploymentInfo {
	for deploymentName, deploymentInfo := range deploymentInfos {

		parts := strings.Split(deploymentName, ".")
		instanceNumber := parts[len(parts)-1]
		pods, err := clientset.CoreV1().Pods(namespace).List(context.TODO(), metav1.ListOptions{
			LabelSelector: fmt.Sprintf("applicationName=%s,instanceNumber=%s", APP_NAME, instanceNumber),
		})
		if err != nil {
			log.Printf("Error getting pods for deployment %s: %v\n", deploymentName, err)
			continue
		}
		for _, pod := range pods.Items {
			podInfo := PodInfo{
				Name: pod.Name,
			}

			for _, condition := range pod.Status.Conditions {
				switch condition.Type {
				case apiv1.PodReady:
					podInfo.Ready = fmt.Sprint(condition.LastTransitionTime.Time)
				case apiv1.PodInitialized:
					podInfo.Initialized = fmt.Sprint(condition.LastTransitionTime.Time)
				case apiv1.ContainersReady:
					podInfo.ContainersReady = fmt.Sprint(condition.LastTransitionTime.Time)
				case apiv1.PodScheduled:
					podInfo.PodScheduled = fmt.Sprint(condition.LastTransitionTime.Time)
				case apiv1.PodReadyToStartContainers:
					podInfo.PodReadyToStartContainers = fmt.Sprint(condition.LastTransitionTime.Time)
				}
			}

			deploymentInfos[deploymentName] = DeploymentInfo{
				DeploymentTime: deploymentInfo.DeploymentTime,
				PodInfo:        podInfo,
			}
		}
	}

	return deploymentInfos
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

	APP_NAME = appName

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

	print(s)

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
	fmt.Println(url)

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

func undeployOakestra(numberOfServices int) map[string]time.Time {
	token, _ := getLogin()

	deploymentInfos := make(map[string]time.Time)

	client := &http.Client{}
	for i := 0; i < numberOfServices; i++ {

		url := fmt.Sprintf("http://%s/api/service/%s/instance/%d", SYSTEM_MANAGER_URL, CLIENT_SERVICE_ID, i)

		req, err := http.NewRequest("DELETE", url, nil)
		if err != nil {
			fmt.Printf("Failed to create DELETE request: %v\n", err)
			os.Exit(1)
		}
		req.Header.Set("Authorization", "Bearer "+token)
		_, err = client.Do(req)
		if err != nil {
			fmt.Printf("Failed to send DELETE request: %v\n", err)
			os.Exit(1)
		}

		deploymentInfos[DEPLOYMENT_BASE_NAME+strconv.Itoa(i)] = time.Now()
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
