##  Deployment-Undeployment Evaluation - Oakestra Kubernertes Plugin

This repository is dedicated to the testing of deployment and undeployment processes across various technologies. Each technology has its own designated folder containing scripts tailored for that specific platform.

#### Usage

To utilize this repository effectively, users are required to construct their own testbeds. Detailed guidelines on the expected setup and configurations will be defined shortly.

#### Evaluation

This repository serves as an essential component for the evaluation of Jakob Kempter's Master's thesis. The tests conducted herein will contribute significantly to the assessment of the thesis's objectives and outcomes.



Cooldown von 60 Sekunden sind wichtig! 
Image wird nicht gelöscht, das darf im cache liegen bleiben. 


karmadactl muss installiert sein!
Es muss auch die Karmada Config sichtbar sein. 





Das mit dem Controller hinzugefügt werden: 
// Delpoyment Test

				ReadinessProbe: &corev1.Probe{
					ProbeHandler: corev1.ProbeHandler{
						HTTPGet: &corev1.HTTPGetAction{
							Path: "/ready",
							Port: intstr.FromInt(7070),
						},
					},
					InitialDelaySeconds: 0,
					PeriodSeconds:       1,
					SuccessThreshold:    1,
				},
				//Delpoyment Test
                


und das hier für den Oakestra Test: 


deployment.Spec.Template.Annotations = map[string]string{
			"k8s.v1.cni.cncf.io/networks": "oakestra-cni",
			"oakestra.io/port":            oakestraJob.Spec.Port,
			// Delpoyment Test
			"deploymentName": deployment.Name,
			// Delpoyment Test
		}