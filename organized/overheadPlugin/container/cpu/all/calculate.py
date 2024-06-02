import os
import pandas as pd

# Funktion zur Berechnung des Durchschnitts der Werte pro Pod und zur Gruppierung nach Namespace
def process_csv_file(filepath, special_namespaces):
    data = pd.read_csv(filepath)
    
    # Berechne den Durchschnitt des Values für jeden Pod
    average_values_per_pod = data.groupby('pod')['value'].mean().reset_index()
    
    # Füge die Namespace-Informationen zu den durchschnittlichen Pod-Daten hinzu
    average_values_per_pod = average_values_per_pod.merge(data[['pod', 'namespace']].drop_duplicates(), on='pod')
    
    # Gruppiere und addiere die Durchschnittswerte
    special_sum, other_sum = group_and_sum_by_namespace(average_values_per_pod, special_namespaces)
    
    return special_sum, other_sum

# Funktion zur Gruppierung und Addition der Durchschnittswerte
def group_and_sum_by_namespace(data, special_namespaces):
    # Pods in speziellen Namespaces
    special_pods = data[data['namespace'].isin(special_namespaces)]
    # Pods nicht in speziellen Namespaces
    other_pods = data[~data['namespace'].isin(special_namespaces)]
    
    # Durchschnittswerte für spezielle Namespaces addieren
    special_sum = special_pods['value'].sum()
    # Durchschnittswerte für andere Namespaces addieren
    other_sum = other_pods['value'].sum()
    
    return special_sum, other_sum

# Definiere die speziellen Namespaces für jedes Verzeichnis
directories_and_namespaces = {
    'oakestra': ['oakestra-system'],
    'karmada': ['karmada-system'],
    'ocm': ['open-cluster-management-agent', 'open-cluster-management']
}

# Liste zur Speicherung der Durchschnittswerte aus allen Dateien
results = []

# Durchlaufe alle angegebenen Verzeichnisse und deren speziellen Namespaces
for directory, special_namespaces in directories_and_namespaces.items():
    # Pfad zum Verzeichnis mit den CSV-Dateien
    directory_path = os.path.join(directory)
    
    # Listen zur Speicherung der Durchschnittswerte pro Verzeichnis
    special_sums = []
    other_sums = []
    
    # Durchlaufe alle CSV-Dateien im angegebenen Verzeichnis
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory_path, filename)
            special_sum, other_sum = process_csv_file(filepath, special_namespaces)
            special_sums.append(special_sum)
            other_sums.append(other_sum)
    
    # Berechne den Durchschnitt der Gesamtsummen aller Dateien im aktuellen Verzeichnis
    final_special_sum = sum(special_sums) / len(special_sums)
    final_other_sum = sum(other_sums) / len(other_sums)
    
    # Ergebnisse für das aktuelle Verzeichnis zur Ergebnisliste hinzufügen
    results.append({'directoryname': directory, 'pod-type': 'Framework Pods', 'value': final_special_sum})
    results.append({'directoryname': directory, 'pod-type': 'Other Pods', 'value': final_other_sum})

# Ergebnisse in einem DataFrame speichern
results_df = pd.DataFrame(results)

# Speichere die Ergebnisse in einer CSV-Datei
results_df.to_csv('grouped_average_values.csv', index=False)

print('CSV-Datei gespeichert: grouped_average_values.csv')
