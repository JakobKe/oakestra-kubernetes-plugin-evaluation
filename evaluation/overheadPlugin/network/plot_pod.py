import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Funktion zur Bereinigung der Pod-Namen
def clean_pod_name(pod_name):
    parts = pod_name.split('-')
    if len(parts) > 2:
        return '-'.join(parts[:-2])
    else:
        return pod_name

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Regex-Filter für Namespaces angeben
namespace_pattern = r'.*'  # Füge hier die gewünschten Regex-Muster hinzu

# Daten nach den erlaubten Namespaces filtern
filtered_data = data[data['namespace'].str.contains(namespace_pattern, regex=True)]

# Pod-Namen bereinigen
filtered_data['clean_pod'] = filtered_data['pod'].apply(clean_pod_name)

# Framework-Namen ändern
filtered_data['framework'] = filtered_data['framework'].replace({'oakestra': 'K-oakestra'})

# Pod-Namen mit Framework kombinieren
filtered_data['framework_pod'] = filtered_data['framework'] + ' - ' + filtered_data['clean_pod']

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Wähle die 20 Pods mit den höchsten Werten für Bytes aus
sorted_bytes_data = bytes_data.groupby('framework_pod')['value'].sum().reset_index().nlargest(20, 'value')
bytes_data = bytes_data[bytes_data['framework_pod'].isin(sorted_bytes_data['framework_pod'])]

# Wähle die 20 Pods mit den höchsten Werten für Packets aus
sorted_packets_data = packets_data.groupby('framework_pod')['value'].sum().reset_index().nlargest(20, 'value')
packets_data = packets_data[packets_data['framework_pod'].isin(sorted_packets_data['framework_pod'])]

# Summe der Werte für jeden Pod und Typ berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()

# Bytes in Megabytes umrechnen
sum_bytes_data['value'] = sum_bytes_data['value'] / (1024 * 1024)

# Daten nach der Summe der Werte sortieren
sum_bytes_data.sort_values(['framework', 'value'], ascending=[True, False], inplace=True)
sum_packets_data.sort_values(['framework', 'value'], ascending=[True, False], inplace=True)

sum_bytes_data['type'] = sum_bytes_data['type'].str.replace('_', ' ')
sum_packets_data['type'] = sum_packets_data['type'].str.replace('_', ' ')

# Variablen für die Anpassung der Schrift- und Legenden-Größe
label_font_size = 16
legend_font_size = 'x-large'
title_font_size = 'x-large'

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, ylabel, filename, palette, hue_order):
    plt.rcParams.update({'font.size': label_font_size})
    plt.figure(figsize=(16, 10))
    sns.barplot(x='framework_pod', y='value', hue='type', data=data, ci=None, palette=palette, hue_order=hue_order)
    plt.xlabel('Pod', fontsize=label_font_size+4)
    plt.ylabel(ylabel, fontsize=label_font_size+4)
    plt.legend(title='Type', loc='upper right', fontsize=legend_font_size, title_fontsize=title_font_size)
    plt.xticks(rotation=90)  # Drehe die x-Achsen-Beschriftungen für bessere Lesbarkeit
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()
    plt.close()

# Farbpalette für "received" und "transmit" definieren mit Hexcodes
palette_bytes = {'received bytes': '#807d59', 'transmit bytes': '#74567a'}
palette_packets = {'received packets': '#807d59', 'transmit packets': '#74567a'}

# Gesamte Datenplots erstellen und speichern
create_and_save_plot(sum_bytes_data,  'Total Bytes (MB)', 'total_bytes_all_frameworks_mb.png', palette_bytes, hue_order=['received bytes', 'transmit bytes'])
create_and_save_plot(sum_packets_data,  'Total Packets', 'total_packets_all_frameworks.png', palette_packets, hue_order=['received packets', 'transmit packets'])

print("Plots gespeichert.")

# Werte für jeden Pod ausgeben
print("\nWerte für jeden Pod:")
for framework_pod, group in filtered_data.groupby('framework_pod'):
    print(f"\n{framework_pod}:")
    received_bytes = group[group['type'] == 'received_bytes']['value'].sum() / (1024 * 1024)
    transmit_bytes = group[group['type'] == 'transmit_bytes']['value'].sum() / (1024 * 1024)
    received_packets = group[group['type'] == 'received_packets']['value'].sum()
    transmit_packets = group[group['type'] == 'transmit_packets']['value'].sum()
    
    print(f"  Received Bytes (MB): {received_bytes:.6f}")
    print(f"  Transmit Bytes (MB): {transmit_bytes:.6f}")
    print(f"  Received Packets: {received_packets}")
    print(f"  Transmit Packets: {transmit_packets}")

# Summen innerhalb eines Frameworks ausgeben
print("\nSummen innerhalb eines Frameworks:")
for framework, group in filtered_data.groupby('framework'):
    print(f"\nFramework: {framework}")
    total_received_bytes = group[group['type'] == 'received_bytes']['value'].sum() / (1024 * 1024)
    total_transmit_bytes = group[group['type'] == 'transmit_bytes']['value'].sum() / (1024 * 1024)
    total_received_packets = group[group['type'] == 'received_packets']['value'].sum()
    total_transmit_packets = group[group['type'] == 'transmit_packets']['value'].sum()
    
    print(f"  Total Received Bytes (MB): {total_received_bytes:.6f}")
    print(f"  Total Transmit Bytes (MB): {total_transmit_bytes:.6f}")
    print(f"  Total Received Packets: {total_received_packets}")
    print(f"  Total Transmit Packets: {total_transmit_packets}")

print("Plots gespeichert.")
