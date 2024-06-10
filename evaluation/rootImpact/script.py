import pandas as pd
import os

# Pfad zum Verzeichnis, das die CSV-Dateien enthält
directory_path = './../../results/impactRoot/1k2o'

# Listen zur Speicherung der Durchschnittswerte
cpu_averages = []
mem_averages = []

# Durchlaufen aller Dateien im Verzeichnis
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        # Einlesen der CSV-Datei
        file_path = os.path.join(directory_path, filename)
        data = pd.read_csv(file_path)
        
        # Bereinigen der Daten
        data['amount_clean'] = data['amount'].replace({'%': '', 'Gi': ''}, regex=True).astype(float)
        
        # Berechnen der Durchschnittswerte für diese Datei
        average_cpu = data[data['type'].str.contains("CPU")]['amount_clean'].mean()
        average_mem = data[data['type'].str.contains("MEM")]['amount_clean'].mean()
        
        # Hinzufügen der Durchschnittswerte zu den Listen
        cpu_averages.append(average_cpu)
        mem_averages.append(average_mem)

# Berechnen des Gesamtdurchschnitts der Durchschnittswerte
overall_average_cpu = sum(cpu_averages) / len(cpu_averages)
overall_average_mem = sum(mem_averages) / len(mem_averages)

# Ausgabe der Gesamtdurchschnittswerte
print(directory_path)
print(f"Gesamtdurchschnittswert für CPU: {overall_average_cpu:.4f}%")
print(f"Gesamtdurchschnittswert für MEM: {overall_average_mem:.2f} Gi")
