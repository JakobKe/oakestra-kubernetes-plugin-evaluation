package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	appsv1 "k8s.io/api/apps/v1"
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

	numDeployments := 4

	replicas := int32(1)

	fmt.Println("Start Deployment...")
	deploy(numDeployments, replicas)

	// fmt.Println("Timer starts...")
	// time.Sleep(5 * time.Second)
	// deploymentInfos = getDeploymentInfo(deploymentInfos)

	// fmt.Println("Delete deployments...")
	// deletedDeployments, err := undeploy(numDeployments)
	// if err != nil {
	// 	log.Fatalf("Failed to delete deployments: %v", err)
	// }

	// fmt.Println(len(deletedDeployments))

	// fmt.Println("Get Finalized Time...")
	// finalizedDeployments, _ := getFinalizedDeployments(deletedDeployments)

	// fmt.Println("Write to CSV")
	// writeInfoToCSV("kubernetes.deploy.undeploy.csv", deploymentInfos, deletedDeployments, finalizedDeployments)
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

func deploy(numDeployments int, replicas int32) map[string]DeploymentInfo {
	deploymentInfos := make(map[string]DeploymentInfo)
	for i := 1; i <= numDeployments; i++ {
		deploymentName := fmt.Sprintf("nginx-deployment-%d", i)
		deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)

		deployment := &appsv1.Deployment{
			ObjectMeta: metav1.ObjectMeta{
				Name: deploymentName,
				Labels: map[string]string{
					"evaluation": "test",
				},
			},

			Spec: appsv1.DeploymentSpec{
				Replicas: &replicas,
				Selector: &metav1.LabelSelector{
					MatchLabels: map[string]string{
						"app":        deploymentName,
						"evaluation": "test",
					},
				},
				Template: apiv1.PodTemplateSpec{
					ObjectMeta: metav1.ObjectMeta{
						Labels: map[string]string{
							"app":        deploymentName,
							"evaluation": "test",
						},
					},
					Spec: apiv1.PodSpec{
						Containers: []apiv1.Container{
							{
								Name:  "gosigterm",
								Image: "ghcr.io/jakobke/oakestra/go-sigterm:latest",
							},
						},
					},
				},
			},
		}

		result, err := deploymentsClient.Create(context.TODO(), deployment, metav1.CreateOptions{})
		if err != nil {
			log.Fatal(err)
		}

		deploymentInfos[result.GetObjectMeta().GetName()] = DeploymentInfo{
			DeploymentTime: time.Now(),
		}
	}
	return deploymentInfos
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

func undeploy(numDeployments int) (map[string]time.Time, error) {
	deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)
	deletedDeployments := map[string]time.Time{}

	for i := 1; i <= numDeployments; i++ {
		deploymentName := fmt.Sprintf("nginx-deployment-%d", i)
		err := deploymentsClient.Delete(context.TODO(), deploymentName, metav1.DeleteOptions{})
		if err != nil {
			log.Printf("error deleting deployment %s: %v", deploymentName, err)
			continue
		}
		deletedDeployments[deploymentName] = time.Now()
	}

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
