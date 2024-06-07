import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('grouped_average_values.csv')

# Berechne die Summe der Werte für jedes Framework
data_sum = data.groupby('directoryname')['value'].sum().reset_index()

# Bereite die Daten für das Plotten vor
data_pivot = data.pivot(index='directoryname', columns='pod-type', values='value').reset_index()
data_pivot['total'] = data_pivot['Framework Pods'] + data_pivot['Other Pods']

# Sortiere die Daten nach der Gesamtsumme für eine bessere Darstellung
data_pivot = data_pivot.sort_values('total', ascending=False)

print(data_pivot)

# Balkendiagramm erstellen
plt.figure(figsize=(12, 8))

# Gestapelte Balken für die Pod-Typen hinzufügen
bottom_plot = plt.bar(data_pivot['directoryname'], data_pivot['Other Pods'], color='r', label='Other Pods')
top_plot = plt.bar(data_pivot['directoryname'], data_pivot['Framework Pods'], bottom=data_pivot['Other Pods'], color='b', label='Framework Pods')

# Titel und Labels hinzufügen
plt.xlabel('Framework')
plt.ylabel('Total CPU Usage')
plt.legend()

# Diagramm speichern
plt.tight_layout()
plt.savefig('total_cpu_usage_by_framework.png')

# Diagramm anzeigen
plt.show()

print("Gestapelter Plot gespeichert und angezeigt.")

# Zusätzlicher Plot: Summe aller Werte pro Framework
plt.figure(figsize=(12, 8))

# Balkendiagramm für die Gesamtsumme der Werte pro Framework erstellen
plt.bar(data_sum['directoryname'], data_sum['value'], color='g')

# Titel und Labels hinzufügen
plt.xlabel('Framework')
plt.ylabel('Total CPU Usage')
plt.title('Total CPU Usage by Framework')

# Diagramm speichern
plt.tight_layout()
plt.savefig('total_cpu_usage_by_framework_sum.png')

# Diagramm anzeigen
plt.show()

print("Gesamtwert-Plot gespeichert und angezeigt.")
