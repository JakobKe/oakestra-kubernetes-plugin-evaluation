import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Daten aus der CSV-Datei einlesen
data = pd.read_csv('pod_cpu_usage_of_component.csv')

# Bereinige die Pod-Namen mit einer Ausnahme für "node-netmanager" und "overhead"
def clean_pod_name(pod_name):
    if "node-netmanager" in pod_name:
        return "node-netmanager"  # Aggregiert alle node-netmanager Pods
    # elif "overhead" in pod_name:
    #     return None  # Entfernt Pods mit "overhead" im Namen
    else:
        parts = pod_name.split('-')
        if len(parts) > 2:
            return '-'.join(parts[:-2])  # Entfernt ab dem vorletzten Bindestrich
        else:
            return pod_name

# Anwenden der Bereinigungsfunktion auf die Pod-Spalte
data['Pod'] = data['Pod'].apply(clean_pod_name)

# Entfernen der Zeilen mit 'None' (Pods mit "overhead" im Namen)
data = data.dropna()

# Entfernen der Zeilen, deren Wert unter 0.01 liegt
data = data[data['CPU_Usage_Average'] >= 0.01]

# Aggregiere die Daten für node-netmanager Pods
node_netmanager_avg = data[data['Pod'] == 'node-netmanager'][['CPU_Usage_Average', 'CPU_Usage_Variance']].mean()
node_netmanager_row = pd.DataFrame({
    'framework': ['oakestra'],
    'Pod': ['node-netmanager'],
    'CPU_Usage_Average': [node_netmanager_avg['CPU_Usage_Average']],
    'CPU_Usage_Variance': [node_netmanager_avg['CPU_Usage_Variance']]
})

# Füge die aggregierten Daten wieder zu den Hauptdaten hinzu
data = data[data['Pod'] != 'node-netmanager']  # Entferne ursprüngliche node-netmanager Einträge
data = pd.concat([data, node_netmanager_row], ignore_index=True)

# Sortiere die Daten nach CPU-Verbrauch für eine ansprechendere Darstellung
data.sort_values('CPU_Usage_Average', ascending=False, inplace=True)

# Farbeinstellungen für spezifische Frameworks mit Hex-Codes
framework_colors = {
    'oakestra': '#666f21',  # Grün
    'kubernetes': '#266f21',  # Grün
    'ocm': '#ffc000',       # Orange
    'karmada': '#bf4129'    # Blau
}

plt.rcParams.update({'font.size': 14})

# Balkendiagramm erstellen für den CPU-Verbrauch jedes Pods
plt.figure(figsize=(18, 8))  # Größe des Diagramms anpassen
bar_plot = sns.barplot(x='Pod', y='CPU_Usage_Average', hue='framework', data=data, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Pod', fontsize=16)
plt.ylabel('CPU Usage Rate [1m]', fontsize=16)
plt.xticks(rotation=45, ha='right')  # Dreht die X-Achsen-Beschriftungen für bessere Lesbarkeit

# Legende anpassen und in die Grafik integrieren
plt.legend(title='Framework', loc='upper right', fontsize='x-large', title_fontsize='x-large')

# Varianz als Fehlerbalken hinzufügen
for i in range(len(data)):
    plt.errorbar(x=i, y=data['CPU_Usage_Average'].iloc[i], yerr=data['CPU_Usage_Variance'].iloc[i], fmt='none', c='black')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('cpu_usage_average_by_pod.png')
plt.show()

# Zweites Diagramm: Gesamtnutzung pro Framework
plt.figure(figsize=(10, 6))
total_usage = data.groupby('framework')['CPU_Usage_Average'].sum().reset_index()
total_usage_plot = sns.barplot(x='framework', y='CPU_Usage_Average', data=total_usage, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Framework', fontsize=16)
plt.ylabel('CPU Usage Rate [1m]', fontsize=16)

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('total_cpu_usage_average_by_framework.png')
plt.show()

print("Plots gespeichert und angezeigt.")
