import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Zusammengefasste CSV-Datei einlesen
data = pd.read_csv('combined_summary_output.csv')

# Daten für Pods, deren Namen mit 'kube-multus' beginnen, herausfiltern
data = data[~data['pod'].str.startswith('kube-multus')]

# Namen der Namespaces klassifizieren
namespace_classification = {
    'kube-system': 'system',
    'oakestra-system': 'plugin',
    'karmada-system': 'plugin',
    'kube-prometheus-stack': 'system',
    'oakestra-controller-manager': 'plugin',
    'open-cluster-management': 'plugin',
    'open-cluster-management-agent': 'plugin',
    # Fügen Sie hier weitere Namespace-Klassifikationen hinzu
}

# Neue Spalte für die Klassifikation der Namespaces hinzufügen
data['namespace_type'] = data['namespace'].map(namespace_classification)

# Filtern, um nur die gewünschten Namespaces einzuschließen
data = data[~data['namespace'].isin(['default', 'oakestra']) & data['namespace_type'].notnull()]

# Daten auf 'kube-system' Namespace filtern
kube_system_data = data[data['namespace'] == 'kube-system']

# Daten für Pods, deren Namen mit 'kube-apiserver', 'etcd' oder 'kube-controller-manager' beginnen, filtern
filtered_pods = kube_system_data[
    kube_system_data['pod'].str.startswith(('kube-apiserver', 'etcd', 'kube-controller-manager'))
]

# "-kubernetes-1" von den Podnamen entfernen
filtered_pods['pod'] = filtered_pods['pod'].str.replace('-kubernetes-1', '')

# Framework-Namen ändern
filtered_pods['framework'] = filtered_pods['framework'].replace({'oakestra': 'K-oakestra'})

# Plot erstellen
plt.figure(figsize=(14, 8))
barplot = sns.barplot(x='framework', y='median', hue='pod', data=filtered_pods, palette='viridis', ci=None)

# Hinzufügen der Standardabweichung als Fehlerbalken
for index, row in filtered_pods.iterrows():
    framework_index = list(filtered_pods['framework'].unique()).index(row['framework'])
    pod_position = list(filtered_pods['pod'].unique()).index(row['pod'])
    barplot.errorbar(x=framework_index + pod_position * 0.25 - 0.25, y=row['median'], yerr=row['std'], fmt='none', c='black', capsize=5)

# Variablen für die Anpassung der Schrift- und Legenden-Größe
label_font_size = 20
legend_font_size = 'large'
title_font_size = 'large'

plt.rcParams.update({'font.size': label_font_size})

# Titel und Labels hinzufügen
plt.xlabel('Framework', fontsize=label_font_size)
plt.ylabel('CPU Usage', fontsize=label_font_size)
plt.legend(title='Pod', loc='upper right', fontsize=legend_font_size, title_fontsize=title_font_size)
plt.ylim(0, filtered_pods['median'].max() + 0.05)
plt.xticks(rotation=0, ha='center', fontsize=20)
plt.yticks(rotation=0, fontsize=20)


# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('specific_pods_kube_system_with_std.png')
plt.show()
