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

# Aggregiere die Daten für node-netmanager Pods
node_netmanager_avg = data[data['Pod'] == 'node-netmanager'][['CPU_Usage_Average', 'CPU_Usage_Variance']].mean()
node_netmanager_row = pd.DataFrame({
    'framework': ['K-oakestra'],
    'Pod': ['node-netmanager'],
    'CPU_Usage_Average': [node_netmanager_avg['CPU_Usage_Average']],
    'CPU_Usage_Variance': [node_netmanager_avg['CPU_Usage_Variance']]
})

# Füge die aggregierten Daten wieder zu den Hauptdaten hinzu
data = data[data['Pod'] != 'node-netmanager']  # Entferne ursprüngliche node-netmanager Einträge
data = pd.concat([data, node_netmanager_row], ignore_index=True)

# Framework-Namen ändern
data['framework'] = data['framework'].replace({'oakestra': 'K-oakestra'})

# Sortiere die Daten nach CPU-Verbrauch für eine ansprechendere Darstellung
data.sort_values('CPU_Usage_Average', ascending=False, inplace=True)

# Farbeinstellungen für spezifische Frameworks mit Hex-Codes
framework_colors = {
    'K-oakestra': '#666f21',  # Grün
    'ocm': '#ffc000',         # Orange
    'karmada': '#bf4129'      # Blau
}

# Variablen für die Anpassung der Schrift- und Legenden-Größe
label_font_size = 22
legend_font_size = 'x-large'
title_font_size = 'x-large'

plt.rcParams.update({'font.size': label_font_size})

# Balkendiagramm erstellen für den CPU-Verbrauch jedes Pods
plt.figure(figsize=(18, 8))
bar_plot = sns.barplot(x='Pod', y='CPU_Usage_Average', hue='framework', data=data, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Pod', fontsize=label_font_size)
plt.ylabel('CPU Usage Rate [1m]', fontsize=label_font_size)
plt.ylim(0, 0.012)
plt.xticks(rotation=45, ha='right')

# Legende anpassen und in die Grafik integrieren
plt.legend(title='Framework', loc='upper right', fontsize=legend_font_size, title_fontsize=title_font_size)

# Varianz als Fehlerbalken hinzufügen
for i in range(len(data)):
    cpu_avg = data['CPU_Usage_Average'].iloc[i]
    cpu_var = data['CPU_Usage_Variance'].iloc[i]
    if cpu_var < 0:
        cpu_var = 0  # Sicherstellen, dass die Varianz nicht negativ ist
    lower_bound = max(0, cpu_avg - cpu_var)  # Fehlerbalken dürfen nicht negativ sein
    upper_bound = cpu_avg + cpu_var
    plt.errorbar(x=i, y=cpu_avg, yerr=[[cpu_avg - lower_bound], [upper_bound - cpu_avg]], fmt='none', c='black')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('cpu_usage_average_by_pod.png')
plt.show()

# Zweites Diagramm: Gesamtnutzung pro Framework
plt.figure(figsize=(10, 6))
total_usage = data.groupby('framework')['CPU_Usage_Average'].sum().reset_index()

total_usage_plot = sns.barplot(x='framework', y='CPU_Usage_Average', data=total_usage, palette=framework_colors)

# Titel und Labels hinzufügen
plt.xlabel('Framework', fontsize=label_font_size)
plt.ylabel('CPU Usage Rate [1m]', fontsize=label_font_size)
plt.ylim(0, 0.02)

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('total_cpu_usage_average_by_framework.png')
plt.show()

print("Plots gespeichert und angezeigt.")
