import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Framework-Namen ändern
data['framework'] = data['framework'].replace({'oakestra': 'K-Oakestra'})

# Daten für Bytes und Pakete filtern
bytes_data = data[data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = data[data['type'].isin(['received_packets', 'transmit_packets'])]

# Bytes in Megabytes umrechnen
bytes_data['value'] = bytes_data['value'] / (1024 * 1024)

# Summe der Werte für jeden Typ und jedes Framework berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'type'])['value'].sum().reset_index()

# Farbpalette für "received" und "transmit" definieren mit Hexcodes
palette_bytes = {'received bytes': '#807d59', 'transmit bytes': '#74567a'}
palette_packets = {'received packets': '#807d59', 'transmit packets': '#74567a'}

# Felder in der Legende ohne Unterstrich umbenennen
sum_bytes_data['type'] = sum_bytes_data['type'].str.replace('_', ' ')
sum_packets_data['type'] = sum_packets_data['type'].str.replace('_', ' ')

# Variablen für die Anpassung der Schrift- und Legenden-Größe
label_font_size = 20
legend_font_size = 'x-large'
title_font_size = 'x-large'

plt.rcParams.update({'font.size': label_font_size})

# Plot für Bytes (in MB) erstellen und speichern
plt.figure(figsize=(14, 8))
sns.barplot(x='framework', y='value', hue='type', data=sum_bytes_data, palette=palette_bytes)
plt.xlabel('Framework', fontsize=label_font_size)
plt.ylabel('Total Bytes (MB)', fontsize=label_font_size)
plt.legend(title='Type', loc='upper right', fontsize=legend_font_size, title_fontsize=title_font_size)
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_bytes_all_frameworks_mb.png')  # Plot speichern
plt.show()

# Plot für Packete erstellen und speichern
plt.figure(figsize=(14, 8))
sns.barplot(x='framework', y='value', hue='type', data=sum_packets_data, palette=palette_packets)
plt.xlabel('Framework', fontsize=label_font_size)
plt.ylabel('Total Packets', fontsize=label_font_size)
plt.legend(title='Type', loc='upper right', fontsize=legend_font_size, title_fontsize=title_font_size)
plt.tight_layout()  # Layout anpassen
plt.savefig('frameworks_total_packets_all_frameworks.png')  # Plot speichern
plt.show()
