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
namespace_pattern = r'karmada-system|oakestra-system|open.*'  # Füge hier die gewünschten Regex-Muster hinzu

# Daten nach den erlaubten Namespaces filtern
filtered_data = data[data['namespace'].str.contains(namespace_pattern, regex=True)]

# Pod-Namen bereinigen
filtered_data['clean_pod'] = filtered_data['pod'].apply(clean_pod_name)

# Pod "node" aus den Daten ausschließen
# filtered_data = filtered_data[filtered_data['clean_pod'] != 'node']

# Pod-Namen mit Framework kombinieren
filtered_data['framework_pod'] = filtered_data['framework'] + ' - ' + filtered_data['clean_pod']

# Farbpalette für "received" und "transmit" definieren mit Hexcodes
palette_bytes = {'received bytes': '#807d59', 'transmit bytes': '#74567a'}
palette_packets = {'received packets': '#807d59', 'transmit packets': '#74567a'}

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Pod und Typ berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()

# Daten nach der Summe der Werte sortieren
sum_bytes_data['total_value'] = sum_bytes_data.groupby('framework_pod')['value'].transform('sum')
sum_packets_data['total_value'] = sum_packets_data.groupby('framework_pod')['value'].transform('sum')
sorted_sum_bytes_data = sum_bytes_data.sort_values('total_value', ascending=False)
sorted_sum_packets_data = sum_packets_data.sort_values('total_value', ascending=False)

sorted_sum_bytes_data['type'] = sorted_sum_bytes_data['type'].str.replace('_', ' ')
sorted_sum_packets_data['type'] = sorted_sum_packets_data['type'].str.replace('_', ' ')

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, ylabel, filename, palette, hue_order):
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(16, 10))
    sns.barplot(x='framework_pod', y='value', hue='type', data=data, ci=None, palette=palette, hue_order=hue_order)
    plt.xlabel('Pod', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.legend(title='Type', loc='upper right', fontsize='x-large', title_fontsize='x-large')
    plt.xticks(rotation=45)  # Drehe die x-Achsen-Beschriftungen für bessere Lesbarkeit
    plt.tight_layout()  # Layout anpassen
    plt.savefig(filename)  # Plot speichern
    plt.show()

# Reihenfolge der Hue-Elemente festlegen
hue_order_bytes = ['received bytes', 'transmit bytes']
hue_order_packets = ['received packets', 'transmit packets']

# Plot für Bytes (in MB) erstellen und speichern
create_and_save_plot(sorted_sum_bytes_data, 'Total Bytes', 'plugin_pod_total_bytes_all_frameworks.png', palette_bytes, hue_order_bytes)

# Plot für Packete erstellen und speichern
create_and_save_plot(sorted_sum_packets_data, 'Total Packets', 'plugin_pod_total_packets_all_frameworks.png', palette_packets, hue_order_packets)

# Pods für das Framework "oakestra" extrahieren und ausgeben
oakestra_pods = filtered_data[filtered_data['framework'] == 'oakestra']['pod'].unique()
print(f'Pods, die für das Framework "oakestra" zusammengerechnet wurden: {oakestra_pods}')

# Werte für jeden Pod ausgeben
print("\nWerte für jeden Pod:")
for framework_pod, group in filtered_data.groupby('framework_pod'):
    print(f"\n{framework_pod}:")
    received_bytes = group[group['type'] == 'received_bytes']['value'].sum()
    transmit_bytes = group[group['type'] == 'transmit_bytes']['value'].sum()
    received_packets = group[group['type'] == 'received_packets']['value'].sum()
    transmit_packets = group[group['type'] == 'transmit_packets']['value'].sum()
    
    print(f"  Received Bytes: {received_bytes:.0f}")
    print(f"  Transmit Bytes: {transmit_bytes:.0f}")
    print(f"  Received Packets: {received_packets}")
    print(f"  Transmit Packets: {transmit_packets}")

# Summen innerhalb eines Frameworks ausgeben
print("\nSummen innerhalb eines Frameworks:")
for framework, group in filtered_data.groupby('framework'):
    print(f"\nFramework: {framework}")
    total_received_bytes = group[group['type'] == 'received_bytes']['value'].sum()
    total_transmit_bytes = group[group['type'] == 'transmit_bytes']['value'].sum()
    total_received_packets = group[group['type'] == 'received_packets']['value'].sum()
    total_transmit_packets = group[group['type'] == 'transmit_packets']['value'].sum()
    
    print(f"  Total Received Bytes: {total_received_bytes:.0f}")
    print(f"  Total Transmit Bytes: {total_transmit_bytes:.0f}")
    print(f"  Total Received Packets: {total_received_packets}")
    print(f"  Total Transmit Packets: {total_transmit_packets}")

print("Plots gespeichert.")
