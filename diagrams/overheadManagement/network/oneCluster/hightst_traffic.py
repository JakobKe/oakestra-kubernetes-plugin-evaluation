import os
import pandas as pd
import matplotlib.pyplot as plt

# Funktion zur Berechnung der Summe von received und transmitted bytes pro Pod
def calculate_total_bytes(file_received, file_transmit):
    received_data = pd.read_csv(file_received)
    transmit_data = pd.read_csv(file_transmit)
    
    # Berechne die Summe der 'value'-Spalte für jeden Pod, gruppiert nach 'namespace', 'pod' und 'container'
    total_received = received_data.groupby(['namespace', 'pod', 'container'])['value'].sum().reset_index()
    total_transmit = transmit_data.groupby(['namespace', 'pod', 'container'])['value'].sum().reset_index()
    
    # Merge die beiden DataFrames auf 'namespace', 'pod' und 'container'
    total_data = pd.merge(total_received, total_transmit, on=['namespace', 'pod', 'container'], suffixes=('_received', '_transmit'))
    total_data['total_bytes'] = total_data['value_received'] + total_data['value_transmit']
    
    return total_data

# Funktion zur Verarbeitung des Verzeichnisses und Berechnung der Top 5 Pods pro Framework
def process_directory(main_directory, subdirectories):
    top_pods_per_framework = []
    
    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(main_directory, subdirectory)
        if os.path.exists(subdirectory_path):
            file_received = os.path.join(subdirectory_path, 'network_received_bytes.csv')
            file_transmit = os.path.join(subdirectory_path, 'network_transmit_bytes.csv')
            
            if os.path.exists(file_received) and os.path.exists(file_transmit):
                total_data = calculate_total_bytes(file_received, file_transmit)
                total_data['framework'] = main_directory
                top_pods_per_framework.append(total_data)
    
    if top_pods_per_framework:
        combined_data = pd.concat(top_pods_per_framework)
        top_5_pods = combined_data.groupby('framework').apply(lambda x: x.nlargest(5, 'total_bytes')).reset_index(drop=True)
        return top_5_pods
    else:
        return pd.DataFrame()

# Hauptverzeichnisse und Unterverzeichnisse angeben
main_directories = ['oakestra', 'karmada', 'ocm', 'kubernetes']
subdirectories = ['1', '2', '3']

# Liste zur Speicherung der DataFrames mit den Top 5 Pods pro Framework
top_pods_list = []

# Verarbeite jedes Hauptverzeichnis
for main_directory in main_directories:
    top_pods = process_directory(main_directory, subdirectories)
    if not top_pods.empty:
        top_pods_list.append(top_pods)

# Verbinde alle DataFrames aus allen Hauptverzeichnissen
if top_pods_list:
    all_top_pods = pd.concat(top_pods_list)

    # Bestimme die maximale Höhe der y-Achse
    max_y = all_top_pods['total_bytes'].max()

    # Erstelle separate Plots für jedes Framework
    for framework in all_top_pods['framework'].unique():
        framework_data = all_top_pods[all_top_pods['framework'] == framework]
        plt.figure(figsize=(10, 6))
        plt.bar(framework_data['pod'], framework_data['total_bytes'])
        plt.xlabel('Pods')
        plt.ylabel('Total Bytes (Received + Transmit)')
        plt.title(f'Top 5 Traffic Pods in {framework}')
        plt.ylim(0, max_y)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

else:
    print('Keine Daten zum Plotten vorhanden.')
