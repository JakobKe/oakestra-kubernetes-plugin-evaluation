import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('average_values_per_pod.csv')

# Regex-Filter für Namespaces angeben
namespace_pattern = r'.*'  # Füge hier die gewünschten Regex-Muster hinzu

# Daten nach den erlaubten Namespaces filtern
filtered_data = data[data['namespace'].str.contains(namespace_pattern, regex=True)]

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Typ und jedes Framework berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'type'])['value'].sum().reset_index()

# Verwendete Pods für jedes Framework ausgeben
framework_pods = filtered_data.groupby(['framework', 'pod']).size().reset_index().groupby('framework')['pod'].unique().reset_index()
print("Verwendete Pods pro Framework und Pod:")
for index, row in framework_pods.iterrows():
    print(f"Framework: {row['framework']}")
    for pod in row['pod']:
        print(f"  Pod: {pod}")

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, title, ylabel, filename):
    print(data)
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
create_and_save_plot(sum_bytes_data, 'Total Bytes by Type for Each Framework', 'Total Bytes', 'plugin_total_bytes_all_frameworks.png')
create_and_save_plot(sum_packets_data, 'Total Packets by Type for Each Framework', 'Total Packets', 'plugin_total_packets_all_frameworks.png')

print("Plots gespeichert.")
