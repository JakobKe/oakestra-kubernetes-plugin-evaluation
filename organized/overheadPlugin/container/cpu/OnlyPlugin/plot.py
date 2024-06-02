import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('pod_cpu_usage_of_component.csv')

# Bereinige die Pod-Namen mit einer Ausnahme für "node-netmanager"
def clean_pod_name(pod_name):
    if "node-netmanager" in pod_name:
        return pod_name.rsplit('-', 1)[0]  # Entfernt ab dem letzten Bindestrich
    else:
        parts = pod_name.split('-')
        if len(parts) > 2:
            return '-'.join(parts[:-2])  # Entfernt ab dem vorletzten Bindestrich
        else:
            return pod_name

data['Pod'] = data['Pod'].apply(clean_pod_name)

# Sortiere die Daten nach CPU-Verbrauch für eine ansprechendere Darstellung
data.sort_values('CPU_Usage', ascending=False, inplace=True)

# Balkendiagramm erstellen für den CPU-Verbrauch jedes Pods
plt.figure(figsize=(12, 8))  # Größe des Diagramms anpassen
bar_plot = sns.barplot(x='Pod', y='CPU_Usage', hue='framework', data=data)

# Titel und Labels hinzufügen
plt.title('CPU Usage by Pod across Frameworks')
plt.xlabel('Pod')
plt.ylabel('CPU Usage')
plt.xticks(rotation=45)  # Dreht die X-Achsen-Beschriftungen für bessere Lesbarkeit

# Legende anpassen und in die Grafik integrieren
plt.legend(title='Framework', loc='upper right')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('cpu_usage_by_pod.png')
plt.show()

# Zweites Diagramm: Gesamtnutzung pro Framework
plt.figure(figsize=(10, 6))
total_usage = data.groupby('framework')['CPU_Usage'].sum().reset_index()
total_usage_plot = sns.barplot(x='framework', y='CPU_Usage', data=total_usage)

# Titel und Labels hinzufügen
plt.title('Total CPU Usage by Framework')
plt.xlabel('Framework')
plt.ylabel('Total CPU Usage')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('total_cpu_usage_by_framework.png')
plt.show()

print("Plots gespeichert und angezeigt.")
