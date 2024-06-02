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

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, title, ylabel, filename):
    plt.figure(figsize=(14, 8))
    sns.barplot(x='framework', y='value', hue='type', data=data)
    plt.title(title)
    plt.xlabel('Framework')
    plt.ylabel(ylabel)
    plt.legend(title='Type')
    plt.tight_layout()  # Layout anpassen
    plt.savefig(filename)  # Plot speichern
    plt.show()

# Gesamte Datenplots erstellen und speichern
create_and_save_plot(sum_bytes_data, 'Total Bytes by Type for Each Framework and Network Type', 'Total Bytes', 'frameworks_total_bytes_all_frameworks.png')
create_and_save_plot(sum_packets_data, 'Total Packets by Type for Each Framework and Network Type', 'Total Packets', 'frameworks_total_packets_all_frameworks.png')

# Separate Plots für die Frameworks und Network Types erstellen und speichern
frameworks = ['Oakestra', 'OCM', 'Karmada']
network_types = ['kubernetes', 'oakestra']

for framework in frameworks:
    for network_type in network_types:
        framework_network_bytes_data = sum_bytes_data[(sum_bytes_data['framework'].str.lower() == framework.lower()) & (sum_bytes_data['network_type'] == network_type)]
        framework_network_packets_data = sum_packets_data[(sum_packets_data['framework'].str.lower() == framework.lower()) & (sum_packets_data['network_type'] == network_type)]
        
        if not framework_network_bytes_data.empty:
            create_and_save_plot(framework_network_bytes_data, f'Total Bytes by Type for {framework} Framework ({network_type})', 'Total Bytes', f'frameworks_total_bytes_{framework.lower()}_{network_type}.png')
        if not framework_network_packets_data.empty:
            create_and_save_plot(framework_network_packets_data, f'Total Packets by Type for {framework} Framework ({network_type})', 'Total Packets', f'frameworks_total_packets_{framework.lower()}_{network_type}.png')

print("Plots gespeichert.")
