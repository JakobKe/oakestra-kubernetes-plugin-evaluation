package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"sync"
	"text/template"
	"time"

	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
)

var (
	clientset *kubernetes.Clientset
)

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

	numDeployments := 2

	fmt.Println("Start Deployment...")
	deploymentInfos := deployOCM(numDeployments)

	fmt.Println("Start timer for termination...")
	time.Sleep(15 * time.Second)
	deploymentInfos = getDeploymentInfo(deploymentInfos)

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
		deletedDeployments, err := undeployOCM()
		if err != nil {
			errChan <- err
			return
		}
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
	writeInfoToCSV("ocm.deploy.undeploy.csv", deploymentInfos, deletedDeployments, cleanedPods)
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

func deployOCM(numDeployments int) map[string]DeploymentInfo {

	dir := "./deploymentFiles"
	os.MkdirAll(dir, 0755)

	for i := 1; i <= numDeployments; i++ {
		deploymentName := fmt.Sprintf("deploy-undeploy-test-%d", i)
		clusterName := "kubernetes-eval"

		yamlContent, err := createOCMYAML(deploymentName, clusterName, deploymentName)
		if err != nil {
			fmt.Println("Error creating YAML:", err)
			return nil
		}

		// Write the YAML content to a file
		fileName := fmt.Sprintf("%s/%s", dir, deploymentName)
		err = os.WriteFile(fileName, []byte(yamlContent), 0644)
		if err != nil {
			fmt.Println("Error writing to file:", err)
			return nil
		}
	}

	return applyYAMLFilesInFolder(dir)
}

func deleteYAMLFilesInFolder(folder string) map[string]time.Time {
	deletedDeployments := make(map[string]time.Time)

	files, err := os.ReadDir(folder)
	if err != nil {
		fmt.Println("failed to read directory: %w", err)
	}

	for _, file := range files {

		filePath := folder + "/" + file.Name()
		execYAMLFile(filePath, "delete")
		deletedDeployments[file.Name()] = time.Now()

	}

	return deletedDeployments
}

func applyYAMLFilesInFolder(folder string) map[string]DeploymentInfo {
	deploymentInfos := make(map[string]DeploymentInfo)

	files, err := os.ReadDir(folder)
	if err != nil {
		fmt.Println("failed to read directory: %w", err)
	}

	for _, file := range files {

		filePath := folder + "/" + file.Name()
		execYAMLFile(filePath, "apply")
		deploymentInfos[file.Name()] = DeploymentInfo{
			DeploymentTime: time.Now(),
		}

	}

	return deploymentInfos
}

func execYAMLFile(filePath string, command string) {
	context := "kubernetes-admin@kubernetes"
	cmd := exec.Command("kubectl", "--kubeconfig", "./ocm.config", command, "-f", filePath, "--context", context)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
		fmt.Println(output)
		return
	}
}

func getFinalizedDeployments(deletedDeployments map[string]int) (map[string]time.Time, error) {
	cleanedPods := map[string]time.Time{}

	for {
		pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
			LabelSelector: "evaluation=test",
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

func undeployOCM() (map[string]time.Time, error) {
	dir := "./deploymentFiles"
	deletedDeployments := deleteYAMLFilesInFolder(dir)

	return deletedDeployments, nil
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

func getDeploymentInfo(deploymentInfos map[string]DeploymentInfo) map[string]DeploymentInfo {
	for deploymentName, deploymentInfo := range deploymentInfos {

		pods, err := clientset.CoreV1().Pods("default").List(context.TODO(), metav1.ListOptions{
			LabelSelector: fmt.Sprintf("app=%s", deploymentName),
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

const yamlTemplate = `
apiVersion: work.open-cluster-management.io/v1
kind: ManifestWork
metadata:
  namespace: {{ .ClusterName }}
  name: {{ .ManifestName }}
spec:
  workload:
    manifests:
      - apiVersion: apps/v1
        kind: Deployment
        metadata:
          namespace: default
          name: {{ .Name }}
          labels:
            app: {{ .Name }}
            evaluation: test
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: {{ .Name }}
              evaluation: test
          template:
            metadata:
              labels:
                app: {{ .Name }}
                evaluation: test
            spec:
              containers:
                - name: gosigterm
                  image: ghcr.io/jakobke/oakestra/go-sigterm:latest
                  readinessProbe:
                    httpGet:
                      path: "/ready"
                      port: 7070
                    initialDelaySeconds: 0
                    periodSeconds: 1
                    successThreshold: 1
`

type Config struct {
	Name         string
	ClusterName  string
	ManifestName string
}

func createOCMYAML(name, clusterName, manifestName string) (string, error) {
	tmpl, err := template.New("yaml").Parse(yamlTemplate)
	if err != nil {
		return "", fmt.Errorf("failed to create template: %w", err)
	}

	config := Config{
		Name:         name,
		ClusterName:  clusterName,
		ManifestName: manifestName,
	}

	var output strings.Builder
	err = tmpl.Execute(&output, config)
	if err != nil {
		return "", fmt.Errorf("failed to execute template: %w", err)
	}

	return output.String(), nil
}
