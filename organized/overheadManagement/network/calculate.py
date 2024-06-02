import os
import pandas as pd

# Funktion zur Berechnung der Durchschnittswerte pro Pod und Typ
def calculate_average_for_pod(file_path, value_type, network_type):
    data = pd.read_csv(file_path)
    # Berechne den Durchschnittswert der 'value'-Spalte für jeden Pod, gruppiert nach 'namespace', 'pod' und 'container'
    average_per_pod = data.groupby(['namespace', 'pod', 'container'])['value'].mean().reset_index()
    average_per_pod['type'] = value_type
    average_per_pod['network_type'] = network_type
    return average_per_pod

# Funktion zur Berechnung des Durchschnitts für alle CSV-Dateien in einem Unterverzeichnis
def process_subdirectory(subdirectory_path, main_folder_name, network_type):
    file_paths = {
        'received_bytes': os.path.join(subdirectory_path, 'network_received_bytes.csv'),
        'transmit_bytes': os.path.join(subdirectory_path, 'network_transmit_bytes.csv'),
        'received_packets': os.path.join(subdirectory_path, 'network_received_packets.csv'),
        'transmit_packets': os.path.join(subdirectory_path, 'network_transmit_packets.csv')
    }

    # Berechne die Durchschnittswerte für die vier CSV-Dateien
    averages = []
    for value_type, file_path in file_paths.items():
        if os.path.exists(file_path):
            avg_df = calculate_average_for_pod(file_path, value_type, network_type)
            avg_df['framework'] = main_folder_name
            averages.append(avg_df)

    # Verbinde die DataFrames zu einem
    combined_df = pd.concat(averages)
    
    return combined_df

# Hauptverzeichnisse angeben
main_directories = ['oakestra', 'karmada','ocm','kubernetes']

# Unterverzeichnisse
subdirectories = ['1', '2', '3']

# Liste zur Speicherung der DataFrames aus allen Haupt- und Unterverzeichnissen
all_combined_dfs = []

# Verarbeite jedes Hauptverzeichnis und jedes Unterverzeichnis darin
for main_directory in main_directories:
    if main_directory == 'oakestra':
        sub_main_directories = ['kubernetes', 'oakestra']
    else:
        sub_main_directories = ['']

    for sub_main in sub_main_directories:
        for subdirectory in subdirectories:
            if sub_main:
                subdirectory_path = os.path.join(main_directory, sub_main, subdirectory)
                network_type = sub_main if sub_main == 'oakestra' else 'kubernetes'
            else:
                subdirectory_path = os.path.join(main_directory, subdirectory)
                network_type = 'kubernetes'

            if os.path.exists(subdirectory_path):
                combined_df = process_subdirectory(subdirectory_path, main_directory, network_type)
                all_combined_dfs.append(combined_df)

# Verbinde alle DataFrames aus allen Haupt- und Unterverzeichnissen
all_data = pd.concat(all_combined_dfs)

# Berechne den Durchschnittswert für jeden Pod über alle Unterverzeichnisse hinweg
final_average_df = all_data.groupby(['framework', 'namespace', 'pod', 'container', 'type', 'network_type'])['value'].mean().reset_index()

# Speichere die Ergebnisse in einer neuen CSV-Datei
output_file_path = 'average_values_per_pod.csv'
final_average_df.to_csv(output_file_path, index=False)

print(f'CSV-Datei gespeichert: {output_file_path}')
