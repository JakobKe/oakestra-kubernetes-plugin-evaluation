import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Zusammengefasste CSV-Datei einlesen
data = pd.read_csv('combined_summary_output.csv')

# Namespaces 'default' und 'oakestra' ausschließen
data = data[~data['namespace'].isin(['default', 'oakestra','cert-manager'])]

# Kommentieren Sie die obige Zeile aus und heben Sie die folgende Zeile aus, um alle Namespaces einzuschließen
# data = pd.read_csv('combined_summary_output.csv')

# Summe der Medianwerte für jedes Framework und jeden Namespace berechnen
sum_median_values = data.groupby(['framework', 'namespace'])['median'].sum().reset_index()

# Plot erstellen
plt.figure(figsize=(14, 8))
print(data)
sns.barplot(x='framework', y='median', hue='namespace', data=sum_median_values, palette='viridis')

# Titel und Labels hinzufügen
plt.title('Sum of Median Values per Framework and Namespace', fontsize=16)
plt.xlabel('Framework', fontsize=14)
plt.ylabel('Sum of Median Values', fontsize=14)

# Legende anpassen
plt.legend(title='Namespace', loc='upper right', fontsize='large', title_fontsize='x-large')

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('sum_median_values_per_framework_namespace.png')
plt.show()
