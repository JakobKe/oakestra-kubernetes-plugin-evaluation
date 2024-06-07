import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Zusammengefasste CSV-Datei einlesen
data = pd.read_csv('combined_summary_output.csv')

# Daten für Pods, deren Namen mit 'kube-multus' beginnen, herausfiltern
data = data[~data['pod'].str.startswith('kube-multus')]

# Median für jedes Framework berechnen (nach dem Filtern)
kube_multus_median_per_framework = data[data['pod'].str.startswith('kube-multus')].groupby('framework')['median'].median().reset_index()

# Ergebnisse für kube-multus Pods drucken
print("Median values for kube-multus Pods per Framework (filtered out):")
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

# Summe der Medianwerte für Plugin und System pro Framework berechnen
total_median_values = sum_median_values.groupby(['framework', 'namespace_type'])['median'].sum().unstack().fillna(0)
total_median_values['total'] = total_median_values.sum(axis=1)

# Ergebnisse drucken
print("\nTotal median values per Framework for Plugin and System:")
print(total_median_values)

# Filter für kube-system Namespace
kube_system_data = data[data['namespace'] == 'kube-system']

# Frameworks extrahieren
frameworks = kube_system_data['framework'].unique()

# Plot pro Framework erstellen
for framework in frameworks:
    plt.figure(figsize=(14, 8))
    framework_data = kube_system_data[kube_system_data['framework'] == framework]
    framework_data = framework_data.sort_values('pod')  # Sicherstellen, dass die Reihenfolge konsistent ist
    yerr = framework_data['std'].values  # yerr als Array
    print(framework)
    print(framework_data)
    sns.barplot(x='pod', y='median', data=framework_data, palette='viridis')
    plt.errorbar(x=range(len(framework_data)), y=framework_data['median'], yerr=yerr, fmt='none', c='black', capsize=5)  # Fehlerbalken hinzufügen
    plt.title(f'Median Values of Pods in kube-system for {framework}', fontsize=16)
    plt.xlabel('Pod', fontsize=14)
    plt.ylabel('Median Value', fontsize=14)
    plt.ylim(0, 0.14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'median_values_kube_system_{framework}.png')
    plt.show()
