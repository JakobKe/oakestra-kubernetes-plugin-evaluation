import os
import pandas as pd

def calculate_average_values(directory):
    # Dictionary zur Speicherung der durchschnittlichen Werte aller Pods aus allen Dateien
    pod_averages = {}
    
    # Durchlaufe alle Dateien im angegebenen Verzeichnis
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            # Pfad zur aktuellen Datei
            filepath = os.path.join(directory, filename)
            
            # Lese die CSV-Datei ein
            data = pd.read_csv(filepath)
            
            # Berechne den Durchschnittswert für jeden Pod in der Datei
            averages = data.groupby('pod')['value'].mean()
            
            # Füge die Durchschnittswerte zu unserem Dictionary hinzu
            for pod, average in averages.items():
                if pod not in pod_averages:
                    pod_averages[pod] = []
                pod_averages[pod].append(average)
    
    # Berechne den Durchschnitt der Durchschnittswerte für jeden Pod
    for pod in pod_averages:
        pod_averages[pod] = sum(pod_averages[pod]) / len(pod_averages[pod])
    
    return pod_averages

def save_average_of_averages_to_csv(directory_paths):
    # Liste zur Speicherung der Ergebnisse aus allen Verzeichnissen
    all_results = []
    
    # Durchlaufe alle übergebenen Verzeichnisse
    for directory in directory_paths:
        # Berechne die Durchschnittswerte für das aktuelle Verzeichnis
        averages = calculate_average_values(directory)
        
        # Füge das Verzeichnis und die Durchschnittswerte zur Liste hinzu
        for pod, average in averages.items():
            all_results.append({"framework": os.path.basename(directory), "Pod": pod, "CPU_Usage": average})
    
    # Erstelle einen DataFrame aus den gesammelten Ergebnissen
    results_df = pd.DataFrame(all_results)
    
    # Speichere den DataFrame in einer CSV-Datei
    results_df.to_csv('pod_cpu_usage_of_component.csv', index=False)

# Liste der Verzeichnispfade
directories = ['oakestra', 'ocm', 'karmada']
save_average_of_averages_to_csv(directories)
