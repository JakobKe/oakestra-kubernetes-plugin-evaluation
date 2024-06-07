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

# Pods für das Framework "oakestra" extrahieren und ausgeben
oakestra_pods = data[data['framework'] == 'oakestra']['pod'].unique()
print(f'Pods, die für das Framework "oakestra" zusammengerechnet wurden: {oakestra_pods}')

# Werte für jedes Framework ausgeben
frameworks = data['framework'].unique()
for framework in frameworks:
    framework_data = data[data['framework'] == framework]
    received_bytes = framework_data[framework_data['type'] == 'received_bytes']['value'].sum() / (1024 * 1024)
    transmit_bytes = framework_data[framework_data['type'] == 'transmit_bytes']['value'].sum() / (1024 * 1024)
    received_packets = framework_data[framework_data['type'] == 'received_packets']['value'].sum()
    transmit_packets = framework_data[framework_data['type'] == 'transmit_packets']['value'].sum()
    
    print(f'\nFramework: {framework}')
    print(f'Received Bytes (MB): {received_bytes:.2f}')
    print(f'Transmit Bytes (MB): {transmit_bytes:.2f}')
    print(f'Received Packets: {received_packets}')
    print(f'Transmit Packets: {transmit_packets}')

print("Plots gespeichert.")
