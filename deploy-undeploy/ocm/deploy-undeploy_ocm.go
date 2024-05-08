package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
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
	createK8SClient()

	numDeployments := 10

	fmt.Println("Start Deployment...")
	deploymentInfos := deployOCM(numDeployments)

	fmt.Println("Timer starts...")
	time.Sleep(5 * time.Second)
	deploymentInfos = getDeploymentInfo(deploymentInfos)

	fmt.Println("Delete deployments...")
	deletedDeployments, err := undeployOCM()
	if err != nil {
		log.Fatalf("Failed to delete deployments: %v", err)
	}

	// TODO - Das muss noch angepasst werden.
	fmt.Println("Get Finalized Time...")
	finalizedDeployments, _ := getFinalizedDeployments(deletedDeployments)

	fmt.Println("Write to CSV")
	writeInfoToCSV("kubernetes.deploy.undeploy.csv", deploymentInfos, deletedDeployments, finalizedDeployments)
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
		deploymentName := fmt.Sprintf("nginx-deployment-%d", i)
		serviceAccount := fmt.Sprintf("nginx-deployment-sa-%d", i)

		yamlContent, err := createOCMYAML(deploymentName, serviceAccount, deploymentName)
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
	fmt.Println(filePath)
	cmd := exec.Command("kubectl", command, "-f", filePath)
	output, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Println(err)
		fmt.Println(output)
		return
	}

}

func getFinalizedDeployments(deletedDeployments map[string]time.Time) (map[string]time.Time, error) {
	finalizedDeployments := map[string]time.Time{}

	for {
		listOptions := metav1.ListOptions{
			LabelSelector: "evaluation=test",
		}
		deployments, err := clientset.AppsV1().Deployments("default").List(context.TODO(), listOptions)
		if err != nil {
			return nil, fmt.Errorf("error listing deployments: %v", err)
		}

		fmt.Println(len(deployments.Items))
		if len(deployments.Items) == 0 {
			break
		}

		remainingDeploymentNames := make(map[string]struct{})
		for _, deployment := range deployments.Items {
			remainingDeploymentNames[deployment.Name] = struct{}{}
		}

		for deploymentName := range deletedDeployments {
			if _, exists := remainingDeploymentNames[deploymentName]; !exists {
				if _, exists := finalizedDeployments[deploymentName]; !exists {
					finalizedDeployments[deploymentName] = time.Now()
				}
			}
		}
	}

	return finalizedDeployments, nil
}

func undeployOCM() (map[string]time.Time, error) {
	dir := "./deploymentFiles"
	deletedDeployments := deleteYAMLFilesInFolder(dir)

	return deletedDeployments, nil
}

func writeInfoToCSV(csvName string, deploymentInfos map[string]DeploymentInfo, deletedDeployments map[string]time.Time, finalizedDeployments map[string]time.Time) {
	file, err := os.Create(csvName)
	if err != nil {
		log.Fatal("Cannot create file", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"DeploymentName", "PodName", "DeploymentTime", "Initialized", "PodScheduled", "ContainersReady", "Ready", "DeleteTime", "FinalizeDeletionTime"})

	var finalizedTime time.Time

	for key, deploymentInfo := range deploymentInfos {
		if deletedTime, exists := deletedDeployments[key]; exists {

			if finalizedTime, exists = finalizedDeployments[key]; !exists {
				finalizedTime = deletedTime
			}

			err := writer.Write([]string{
				key,
				deploymentInfo.PodInfo.Name,
				deploymentInfo.DeploymentTime.Format(time.RFC3339),
				deploymentInfo.PodInfo.Initialized,
				deploymentInfo.PodInfo.PodScheduled,
				deploymentInfo.PodInfo.ContainersReady,
				deploymentInfo.PodInfo.Ready,
				deletedTime.Format(time.RFC3339),
				finalizedTime.Format(time.RFC3339),
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
			fmt.Println(pod.Name)
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
  namespace: cluster1
  name: {{ .ManifestName }}
spec:
  workload:
    manifests:
      - apiVersion: v1
        kind: ServiceAccount
        metadata:
          namespace: default
          name: {{ .ServiceAccount }}
      - apiVersion: apps/v1
        kind: Deployment
        metadata:
          namespace: default
          name: {{ .Name }}
          labels:
            app: {{ .Name }}
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: {{ .Name }}
          template:
            metadata:
              labels:
                app: {{ .Name }}
            spec:
              serviceAccountName: {{ .ServiceAccount }}
              containers:
                - name: gosigterm
                  image: ghcr.io/jakobke/oakestra/go-sigterm:latest
                  
`

type Config struct {
	Name           string
	ServiceAccount string
	ManifestName   string
}

func createOCMYAML(name, serviceAccount, manifestName string) (string, error) {
	tmpl, err := template.New("yaml").Parse(yamlTemplate)
	if err != nil {
		return "", fmt.Errorf("failed to create template: %w", err)
	}

	config := Config{
		Name:           name,
		ServiceAccount: serviceAccount,
		ManifestName:   manifestName,
	}

	var output strings.Builder
	err = tmpl.Execute(&output, config)
	if err != nil {
		return "", fmt.Errorf("failed to execute template: %w", err)
	}

	return output.String(), nil
}
