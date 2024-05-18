package main

import (
	"context"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sync"
	"time"

	appsv1 "k8s.io/api/apps/v1"
	apiv1 "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/util/intstr"

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

	numDeployments := 300
	fileName := fmt.Sprintf("5_kubernetes_deploy_undeploy_%d.csv", numDeployments)

	replicas := int32(1)

	fmt.Println("Start Deployment...")
	deploymentInfos := deploy(numDeployments, replicas)

	fmt.Println("Timer starts...")
	time.Sleep(30 * time.Second)
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
		deletedDeployments, err := undeploy(numDeployments)
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

	writeInfoToCSV(fileName, deploymentInfos, deletedDeployments, cleanedPods)

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
		deploymentName := fmt.Sprintf("deploy-test-%d", i)
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
								ReadinessProbe: &apiv1.Probe{
									ProbeHandler: apiv1.ProbeHandler{
										HTTPGet: &apiv1.HTTPGetAction{
											Path: "/ready",
											Port: intstr.FromInt(7070),
										},
									},
									InitialDelaySeconds: 0,
									PeriodSeconds:       1,
									SuccessThreshold:    1,
								},
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

func undeploy(numDeployments int) (map[string]time.Time, error) {
	deploymentsClient := clientset.AppsV1().Deployments(apiv1.NamespaceDefault)
	deletedDeployments := map[string]time.Time{}

	for i := 1; i <= numDeployments; i++ {
		deploymentName := fmt.Sprintf("deploy-test-%d", i)
		err := deploymentsClient.Delete(context.TODO(), deploymentName, metav1.DeleteOptions{})
		if err != nil {
			log.Printf("error deleting deployment %s: %v", deploymentName, err)
			continue
		}
		deletedDeployments[deploymentName] = time.Now()
	}

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
