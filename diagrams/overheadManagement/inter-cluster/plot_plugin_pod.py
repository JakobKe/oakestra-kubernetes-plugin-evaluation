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

# Pod-Namen mit Framework kombinieren
filtered_data['framework_pod'] = filtered_data['framework'] + ' - ' + filtered_data['clean_pod']


# Farbpalette für "received" und "transmit" definieren mit Hexcodes
palette_bytes = {'received bytes': '#807d59', 'transmit bytes': '#74567a'}
palette_packets = {'received packets': '#807d59', 'transmit packets': '#74567a'}

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Wähle die 30 Pods mit den höchsten Werten für Bytes aus
sorted_bytes_data = bytes_data.groupby('framework_pod')['value'].sum().reset_index().nlargest(19, 'value')
bytes_data = bytes_data[bytes_data['framework_pod'].isin(sorted_bytes_data['framework_pod'])]

# Wähle die 30 Pods mit den höchsten Werten für Packets aus
sorted_packets_data = packets_data.groupby('framework_pod')['value'].sum().reset_index().nlargest(19, 'value')
packets_data = packets_data[packets_data['framework_pod'].isin(sorted_packets_data['framework_pod'])]



# Summe der Werte für jeden Pod und Typ berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'framework_pod', 'type'])['value'].sum().reset_index()

# Daten nach der Summe der Werte sortieren
sum_bytes_data['total_value'] = sum_bytes_data.groupby('framework_pod')['value'].transform('sum')
sum_packets_data['total_value'] = sum_packets_data.groupby('framework_pod')['value'].transform('sum')
sorted_sum_bytes_data = sum_bytes_data.sort_values('total_value', ascending=False)
sorted_sum_packets_data = sum_packets_data.sort_values('total_value', ascending=False)

sorted_sum_bytes_data['type'] = sum_bytes_data['type'].str.replace('_', ' ')
sorted_sum_packets_data['type'] = sum_packets_data['type'].str.replace('_', ' ')






# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, ylabel, filename, palette):
    print(data)
    plt.rcParams.update({'font.size': 16})
    plt.figure(figsize=(16, 10))
    sns.barplot(x='framework_pod', y='value', hue='type', data=data, ci=None, palette=palette)
    plt.xlabel('Pod', fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.legend(title='Type', loc='upper right', fontsize='x-large', title_fontsize='x-large')
    plt.xticks(rotation=90)  # Drehe die x-Achsen-Beschriftungen für bessere Lesbarkeit
    plt.tight_layout()  # Layout anpassen
    plt.savefig(filename)  # Plot speichern
    plt.show()

# Plot für Bytes erstellen und speichern
create_and_save_plot(sorted_sum_bytes_data, 'Total Bytes', 'plugin_pod_total_bytes_all_frameworks.png', palette_bytes)

# Plot für Packete erstellen und speichern
create_and_save_plot(sorted_sum_packets_data, 'Total Packets', 'plugin_pod_total_packets_all_frameworks.png', palette_packets)

print("Plots gespeichert.")
