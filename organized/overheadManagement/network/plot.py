import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Daten für Bytes und Pakete filtern
bytes_data = data[data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = data[data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Typ, jedes Framework und Network Type berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'type', 'network_type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'type', 'network_type'])['value'].sum().reset_index()

# Frameworks mit mehr als einem Netzwerktyp identifizieren
multi_network_frameworks = data.groupby(['framework', 'network_type']).size().reset_index().groupby('framework').size()
multi_network_frameworks = multi_network_frameworks[multi_network_frameworks > 1].index.tolist()

# Daten aufteilen basierend auf Frameworks mit mehreren Netzwerktypen
sum_bytes_data['category'] = sum_bytes_data.apply(lambda x: f"{x['framework']} ({x['network_type']})" if x['framework'] in multi_network_frameworks else x['framework'], axis=1)
sum_packets_data['category'] = sum_packets_data.apply(lambda x: f"{x['framework']} ({x['network_type']})" if x['framework'] in multi_network_frameworks else x['framework'], axis=1)

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, title, ylabel, filename):
    plt.figure(figsize=(14, 8))
    sns.barplot(x='category', y='value', hue='type', data=data)
    plt.title(title)
    plt.xlabel('Framework and Network Type')
    plt.ylabel(ylabel)
    plt.legend(title='Type')
    plt.tight_layout()  # Layout anpassen
    plt.savefig(filename)  # Plot speichern
    plt.show()

# Plots für Bytes und Pakete erstellen und speichern
create_and_save_plot(sum_bytes_data, 'Total Bytes by Type for Each Framework and Network Type', 'Total Bytes', 'frameworks_total_bytes.png')
create_and_save_plot(sum_packets_data, 'Total Packets by Type for Each Framework and Network Type', 'Total Packets', 'frameworks_total_packets.png')

print("Plots gespeichert.")
