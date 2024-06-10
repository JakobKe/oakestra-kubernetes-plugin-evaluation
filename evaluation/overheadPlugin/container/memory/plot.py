import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Daten aus der CSV-Datei einlesen
data = pd.read_csv('pod_cpu_usage_of_component.csv')

# Bereinige die Pod-Namen mit einer Ausnahme für "node-netmanager"
def clean_pod_name(pod_name):
    if "node-netmanager" in pod_name:
        return "node-netmanager"  # Aggregiert alle node-netmanager Pods
    else:
        parts = pod_name.split('-')
        if len(parts) > 2:
            return '-'.join(parts[:-2])  # Entfernt ab dem vorletzten Bindestrich
        else:
            return pod_name

data['Pod'] = data['Pod'].apply(clean_pod_name)

# CPU Usage in MB umrechnen
data['CPU_Usage_Average_MB'] = data['CPU_Usage_Average'] / (1024 * 1024)
data['CPU_Usage_Variance_MB'] = data['CPU_Usage_Variance'] / (1024 * 1024)

# Aggregiere die Daten für node-netmanager Pods
node_netmanager_avg = data[data['Pod'] == 'node-netmanager'][['CPU_Usage_Average_MB', 'CPU_Usage_Variance_MB']].mean()
node_netmanager_row = pd.DataFrame({
    'framework': ['oakestra'],
    'Pod': ['node-netmanager'],
    'CPU_Usage_Average_MB': [node_netmanager_avg['CPU_Usage_Average_MB']],
    'CPU_Usage_Variance_MB': [node_netmanager_avg['CPU_Usage_Variance_MB']]
})

# Füge die aggregierten Daten wieder zu den Hauptdaten hinzu
data = data[data['Pod'] != 'node-netmanager']  # Entferne ursprüngliche node-netmanager Einträge
data = pd.concat([data, node_netmanager_row], ignore_index=True)

# Sortiere die Daten nach CPU-Verbrauch für eine ansprechendere Darstellung
data.sort_values('CPU_Usage_Average_MB', ascending=False, inplace=True)

# Farbeinstellungen für spezifische Frameworks mit Hex-Codes
framework_colors = {
    'oakestra': '#666f21',  # Grün
    'ocm': '#ffc000',       # Orange
    'karmada': '#bf4129'    # Blau
}

plt.rcParams.update({'font.size': 14})

# Balkendiagramm erstellen für den CPU-Verbrauch jedes Pods
plt.figure(figsize=(18, 8))  # Größe des Diagramms anpassen
print(data)
bar_plot = sns.barplot(x='Pod', y='CPU_Usage_Average_MB', hue='framework', data=data, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Pod', fontsize=16)
plt.ylabel('Working Set Memory (MB)', fontsize=16)
plt.xticks(rotation=45, ha='right')  # Dreht die X-Achsen-Beschriftungen für bessere Lesbarkeit

# Legende anpassen und in die Grafik integrieren
plt.legend(title='Framework', loc='upper right', fontsize='x-large', title_fontsize='x-large')

# Varianz als Fehlerbalken hinzufügen
for i in range(len(data)):
    plt.errorbar(x=i, y=data['CPU_Usage_Average_MB'].iloc[i], yerr=data['CPU_Usage_Variance_MB'].iloc[i], fmt='none', c='black')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('mem_usage_average_by_pod.png')
plt.show()

# Zweites Diagramm: Gesamtnutzung pro Framework
plt.figure(figsize=(10, 6))
total_usage = data.groupby('framework')['CPU_Usage_Average_MB'].sum().reset_index()
print(total_usage)
total_usage_plot = sns.barplot(x='framework', y='CPU_Usage_Average_MB', data=total_usage, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Framework', fontsize=16)
plt.ylabel('Working Set Memory (MB)', fontsize=16)

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('total_mem_usage_average_by_framework.png')
plt.show()

print("Plots gespeichert und angezeigt.")
