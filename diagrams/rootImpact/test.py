import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

# Funktion zum Bereinigen des Dateinamens
def clean_label(file_path):
    base_name = os.path.basename(file_path)
    clean_name = base_name.replace('.csv', '').replace('cpumemoryusage_', '').replace('_', ' ')
    return clean_name

# Liste der CSV-Dateipfade
file_paths = glob.glob('./../../tests/root-impact/*_cpumemoryusage_K1_O0.csv')

cpu_data_list = []
mem_data_list = []

# Daten aus jeder CSV-Datei einlesen und verarbeiten
for file_path in file_paths:
    df = pd.read_csv(file_path)
    
    # Spalte 'amount' bereinigen und konvertieren
    df['amount'] = df['amount'].replace({'%': '', 'Gi': ''}, regex=True).astype(float)
    
    # Index-Spalte für den zeitlichen Verlauf hinzufügen
    df['time'] = range(len(df))
    
    # CPU- und MEM-Daten trennen
    cpu_data = df[df['type'] == '%CPU'].reset_index(drop=True)
    mem_data = df[df['type'] == '%MEM'].reset_index(drop=True)
    
    cpu_data_list.append(cpu_data)
    mem_data_list.append(mem_data)

# Zusammenführen aller CPU-Daten
cpu_combined = pd.concat(cpu_data_list)
mem_combined = pd.concat(mem_data_list)

# Berechnung der minimalen und maximalen Werte für jeden Zeitpunkt
cpu_min = cpu_combined.groupby('time')['amount'].min()
cpu_max = cpu_combined.groupby('time')['amount'].max()
mem_min = mem_combined.groupby('time')['amount'].min()
mem_max = mem_combined.groupby('time')['amount'].max()

# Plot erstellen
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# CPU-Daten plotten
ax1.fill_between(cpu_min.index, cpu_min, cpu_max, color='skyblue', alpha=0.4)
ax1.plot(cpu_min.index, cpu_min, color='blue', label='Min %CPU')
ax1.plot(cpu_min.index, cpu_max, color='blue', label='Max %CPU')
ax1.set_title('%CPU Usage Over Time')
ax1.set_xlabel('Time')
ax1.set_ylabel('%CPU Usage')
ax1.legend()

# MEM-Daten plotten
ax2.fill_between(mem_min.index, mem_min, mem_max, color='lightgreen', alpha=0.4)
ax2.plot(mem_min.index, mem_min, color='green', label='Min %MEM')
ax2.plot(mem_min.index, mem_max, color='green', label='Max %MEM')
ax2.set_title('%MEM Usage Over Time')
ax2.set_xlabel('Time')
ax2.set_ylabel('%MEM Usage')
ax2.legend()

plt.tight_layout()
plt.show()
