import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Zusammengefasste CSV-Datei einlesen
data = pd.read_csv('combined_summary_output.csv')

# Daten für Pods, deren Namen mit 'kube-multus' beginnen, filtern
kube_multus_data = data[data['pod'].str.startswith('kube-multus')]

# Median für jedes Framework berechnen
kube_multus_median_per_framework = kube_multus_data.groupby('framework')['median'].median().reset_index()

# Ergebnisse für kube-multus Pods drucken
print("Median values for kube-multus Pods per Framework:")
print(kube_multus_median_per_framework)

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

# Summe der Medianwerte für jedes Framework und jeden Namespace-Typ berechnen
sum_median_values = data.groupby(['framework', 'namespace_type'])['median'].sum().reset_index()

# Plot erstellen
plt.figure(figsize=(14, 8))
plt.rcParams.update({'font.size': 16})
sns.barplot(x='framework', y='median', hue='namespace_type', data=sum_median_values, palette='viridis')

# Titel und Labels hinzufügen
plt.xlabel('Framework', fontsize=16)
plt.ylabel('CPU Usage', fontsize=16)
plt.ylim(0,0.8)

# Legende anpassen
plt.legend(title='Type', loc='upper right', fontsize='large', title_fontsize='x-large')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('sum_median_values_per_framework_namespace_type.png')
plt.show()

# Summe der Medianwerte für Plugin und System pro Framework berechnen
total_median_values = sum_median_values.groupby(['framework', 'namespace_type'])['median'].sum().unstack().fillna(0)
total_median_values['total'] = total_median_values.sum(axis=1)

# Ergebnisse drucken
print("\nTotal median values per Framework for Plugin and System:")
print(total_median_values)
