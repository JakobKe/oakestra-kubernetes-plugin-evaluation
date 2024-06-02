import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Regex-Filter für Namespaces angeben
namespace_pattern = r'karmada-system|oakestra-system|open.*'  # Füge hier die gewünschten Regex-Muster hinzu

# Daten nach den erlaubten Namespaces filtern
filtered_data = data[data['namespace'].str.contains(namespace_pattern, regex=True)]

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Typ und jedes Framework und Network Type berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'type', 'network_type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'type', 'network_type'])['value'].sum().reset_index()

# Verwendete Pods für jedes Framework und Network Type ausgeben
framework_pods = filtered_data.groupby(['framework', 'network_type', 'pod']).size().reset_index().groupby(['framework', 'network_type'])['pod'].unique().reset_index()
print("Verwendete Pods pro Framework und Pod:")
for index, row in framework_pods.iterrows():
    print(f"Framework: {row['framework']}, Network Type: {row['network_type']}")
    for pod in row['pod']:
        print(f"  Pod: {pod}")

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
create_and_save_plot(sum_bytes_data, 'Total Bytes by Type for Each Framework and Network Type', 'Total Bytes', 'plugin_total_bytes_all_frameworks.png')
create_and_save_plot(sum_packets_data, 'Total Packets by Type for Each Framework and Network Type', 'Total Packets', 'plugin_total_packets_all_frameworks.png')

# Separate Plots für die Frameworks und Network Types erstellen und speichern
frameworks = ['oakestra', 'karmada', 'ocm']
network_types = ['kubernetes', 'oakestra']

for framework in frameworks:
    for network_type in network_types:
        framework_network_bytes_data = sum_bytes_data[(sum_bytes_data['framework'].str.lower() == framework.lower()) & (sum_bytes_data['network_type'] == network_type)]
        framework_network_packets_data = sum_packets_data[(sum_packets_data['framework'].str.lower() == framework.lower()) & (sum_packets_data['network_type'] == network_type)]
        
        if not framework_network_bytes_data.empty:
            create_and_save_plot(framework_network_bytes_data, f'Total Bytes by Type for {framework.capitalize()} Framework ({network_type})', 'Total Bytes', f'plugin_total_bytes_{framework.lower()}_{network_type}.png')
        if not framework_network_packets_data.empty:
            create_and_save_plot(framework_network_packets_data, f'Total Packets by Type for {framework.capitalize()} Framework ({network_type})', 'Total Packets', f'plugin_total_packets_{framework.lower()}_{network_type}.png')

print("Plots gespeichert.")
