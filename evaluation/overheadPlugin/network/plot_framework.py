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

# Bytes in Megabytes umrechnen
sum_bytes_data['value'] = sum_bytes_data['value'] / (1024 * 1024)

# Farbpalette für "received" und "transmit" definieren mit Hexcodes
palette_bytes = {'received bytes': '#807d59', 'transmit bytes': '#74567a'}
palette_packets = {'received packets': '#807d59', 'transmit packets': '#74567a'}

# Felder in der Legende ohne Unterstrich umbenennen
sum_bytes_data['type'] = sum_bytes_data['type'].str.replace('_', ' ')
sum_packets_data['type'] = sum_packets_data['type'].str.replace('_', ' ')

plt.rcParams.update({'font.size': 16})

# Plot für Bytes (in MB) erstellen und speichern
plt.figure(figsize=(14, 8))
print(sum_bytes_data)
sns.barplot(x='framework', y='value', hue='type', data=sum_bytes_data, palette=palette_bytes)
plt.xlabel('Framework', fontsize=16)
plt.ylabel('MB', fontsize=16)
plt.legend(title='Type', loc='upper right', fontsize='x-large', title_fontsize='x-large')
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_bytes_all_frameworks_mb.png')  # Plot speichern
plt.show()

# Plot für Pakete erstellen und speichern
plt.figure(figsize=(14, 8))
sns.barplot(x='framework', y='value', hue='type', data=sum_packets_data, palette=palette_packets)
plt.xlabel('Framework', fontsize=16)
plt.ylabel('Total Packets', fontsize=16)
plt.legend(title='Type', loc='upper right', fontsize='x-large', title_fontsize='x-large')
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_packets_all_frameworks.png')  # Plot speichern
plt.show()
