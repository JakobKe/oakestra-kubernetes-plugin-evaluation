import os
import pandas as pd

def concatenate_csv_files(directory_paths):
    # Liste zur Speicherung aller Daten
    all_data = []
    
    # Durchlaufe alle übergebenen Verzeichnisse
    for directory in directory_paths:
        # Durchlaufe alle Dateien im aktuellen Verzeichnis
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                # Pfad zur aktuellen Datei
                filepath = os.path.join(directory, filename)
                
                # Lese die CSV-Datei ein
                data = pd.read_csv(filepath)
                
                # Füge den Framework-Namen hinzu
                data['framework'] = os.path.basename(directory)
                
                # Füge die Daten zur Liste hinzu
                all_data.append(data)
    
    # Konkateniere alle Daten
    concatenated_data = pd.concat(all_data, ignore_index=True)
    
    return concatenated_data

def calculate_stats(data):
    # Ändere den Pod-Namen für alle Pods, die mit 'oakestra-agent' beginnen, in 'oakestra-agent'
    data['pod'] = data['pod'].apply(lambda x: 'oakestra-agent' if x.startswith('oakestra-agent') else x)
    
    # Berechne den Durchschnitt und die Varianz der CPU-Auslastung für jeden Pod und Framework
    stats = data.groupby(['framework', 'pod'])['value'].agg(['median', 'std']).reset_index()
    stats.columns = ['framework', 'Pod', 'CPU_Usage_Average', 'CPU_Usage_Variance']
    
    return stats

def save_stats_to_csv(stats, filename='pod_cpu_usage_of_component.csv'):
    # Speichere die Statistik-Daten in einer CSV-Datei
    stats.to_csv(filename, index=False)

# Liste der Verzeichnispfade
directories = ['oakestra', 'ocm', 'karmada']

# Konkateniere die CSV-Dateien und berechne die Statistiken
data = concatenate_csv_files(directories)
stats = calculate_stats(data)

# Speichere die Statistiken in einer CSV-Datei
save_stats_to_csv(stats)
