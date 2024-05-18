import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Funktion zum Bereinigen des Dateinamens
def clean_label(file_path):
    base_name = os.path.basename(file_path)
    clean_name = base_name.replace('.csv', '').replace('cpumemoryusage_', '').replace('_', ' ')
    return clean_name

# Funktion zum Reduzieren der Anzahl der Datenpunkte
def reduce_data(df, sample_size=50):
    return df.sample(n=sample_size) if len(df) > sample_size else df

# Liste der CSV-Dateipfade
file_paths = [
    './../../tests/root-impact/cpumemoryusage_K1_O0.csv',
    './../../tests/root-impact/cpumemoryusage_K3_O3.csv',
    './../../tests/root-impact/cpumemoryusage_K5_O1.csv'
]

cpu_data_list = []
mem_data_list = []
labels = []

# Daten aus jeder CSV-Datei einlesen und verarbeiten
for file_path in file_paths:
    df = pd.read_csv(file_path)
    
    # Spalte 'amount' bereinigen und konvertieren
    df['amount'] = df['amount'].replace({'%': '', 'Gi': ''}, regex=True).astype(float)
    
    # Index-Spalte für den zeitlichen Verlauf hinzufügen
    df['time'] = range(len(df))
    
    # CPU- und MEM-Daten trennen und Anzahl der Datenpunkte reduzieren
    cpu_data = reduce_data(df[df['type'] == '%CPU'].reset_index(drop=True))
    mem_data = reduce_data(df[df['type'] == '%MEM'].reset_index(drop=True))
    
    cpu_data_list.append(cpu_data)
    mem_data_list.append(mem_data)
    
    # Labels bereinigen
    labels.append(clean_label(file_path))

# Plot erstellen
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# CPU-Daten plotten
for cpu_data, label in zip(cpu_data_list, labels):
    sns.lineplot(data=cpu_data, x='time', y='amount', marker='o', ax=ax1, label=label)
ax1.set_title('%CPU Usage Over Time')
ax1.set_xlabel('Time')
ax1.set_ylabel('%CPU Usage')
ax1.legend()

# MEM-Daten plotten
for mem_data, label in zip(mem_data_list, labels):
    sns.lineplot(data=mem_data, x='time', y='amount', marker='o', ax=ax2, label=label)
ax2.set_title('%MEM Usage Over Time')
ax2.set_xlabel('Time')
ax2.set_ylabel('%MEM Usage')
ax2.legend()

plt.tight_layout()
plt.show()
