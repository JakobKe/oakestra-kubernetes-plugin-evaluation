import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Zusammengefasste CSV-Datei einlesen
data = pd.read_csv('combined_summary_output.csv')

data = data[~data['namespace'].isin(['default', 'oakestra','cert-manager'])]

# Summe der Medianwerte für jedes Framework berechnen
sum_median_values = data.groupby('framework')['median'].sum().reset_index()

# Plot erstellen
plt.figure(figsize=(12, 6))
sns.barplot(x='framework', y='median', data=sum_median_values, palette='viridis')

# Titel und Labels hinzufügen
plt.title('Sum of Median Values per Framework', fontsize=16)
plt.xlabel('Framework', fontsize=14)
plt.ylabel('Sum of Median Values', fontsize=14)

# Diagramm speichern und anzeigen
plt.tight_layout()
plt.savefig('sum_median_values_per_framework.png')
plt.show()
