import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Daten für Bytes und Pakete filtern
bytes_data = data[data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = data[data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Typ und jedes Framework berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'type'])['value'].sum().reset_index()

# Plot für Bytes erstellen und speichern
plt.figure(figsize=(14, 8))
sns.barplot(x='framework', y='value', hue='type', data=sum_bytes_data)
plt.title('Total Bytes by Type for Each Framework')
plt.xlabel('Framework')
plt.ylabel('Total Bytes')
plt.legend(title='Type')
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_bytes_all_frameworks.png')  # Plot speichern
plt.show()

# Plot für Packete erstellen und speichern
plt.figure(figsize=(14, 8))
sns.barplot(x='framework', y='value', hue='type', data=sum_packets_data)
plt.title('Total Packets by Type for Each Framework')
plt.xlabel('Framework')
plt.ylabel('Total Packets')
plt.legend(title='Type')
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_packets_all_frameworks.png')  # Plot speichern
plt.show()