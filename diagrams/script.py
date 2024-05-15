
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os



# CSV-Dateien einlesen
csv_file1 = './../metrics/results/cpu_container/container_cpu_usage_seconds_total.csv'
csv_file2 = './../metrics/results/cpu_container/container_cpu_usage_seconds_total.csv'

data1 = pd.read_csv(csv_file1)
data2 = pd.read_csv(csv_file2)

# Zeitstempel in eine fortlaufende Zeitreihe umwandeln
data1['time'] = range(len(data1))
data2['time'] = range(len(data2))

# Diagramm mit Seaborn erstellen
plt.figure(figsize=(10, 6))

# Erste Datenreihe plotten
sns.lineplot(x='time', y='value', data=data1, label='Kubernetes')

# Zweite Datenreihe plotten
sns.lineplot(x='time', y='value', data=data2, label='Oakestra Plugin', color='green')

# Diagramm anpassen und anzeigen
plt.ylim(0, 2)  # Y-Achse Bereich setzen
plt.title('Total Container CPU Usage in 5 Minutes')
plt.xlabel('time')
plt.ylabel('value')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()


save_dir = 'results/cpu_container'  
file_name = 'cpu_usage_total.png'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Datei speichern
file_path = os.path.join(save_dir, file_name)
plt.savefig(file_path)
plt.show()

