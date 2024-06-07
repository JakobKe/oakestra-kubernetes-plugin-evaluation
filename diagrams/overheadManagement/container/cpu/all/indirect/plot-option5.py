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

# Daten für Pods, deren Namen mit 'node-netmanager' beginnen, filtern
node_netmanager_data = data[(data['framework'] == 'oakestra') & data['pod'].str.startswith('node-netmanager')]

# Summe der Medianwerte für node-netmanager Pods berechnen
sum_node_netmanager_median = node_netmanager_data.groupby('pod')['median'].sum().reset_index()

# Plot erstellen
plt.figure(figsize=(14, 8))
print(sum_node_netmanager_median)
sns.barplot(x='pod', y='median', data=sum_node_netmanager_median, palette='viridis')

# Titel und Labels hinzufügen
plt.title('Sum of Median Values for node-netmanager Pods in Oakestra', fontsize=16)
plt.xlabel('Pod', fontsize=14)
plt.ylabel('Sum of Median Values', fontsize=14)
plt.ylim(0, 0.14)
plt.xticks(rotation=45, ha='right')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('sum_median_values_node_netmanager_oakestra.png')
plt.show()
