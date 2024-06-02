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

# Daten für Bytes und Pakete filtern
bytes_data = filtered_data[filtered_data['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_data = filtered_data[filtered_data['type'].isin(['received_packets', 'transmit_packets'])]

# Summe der Werte für jeden Pod und Typ berechnen
sum_bytes_data = bytes_data.groupby(['framework', 'framework_pod', 'type', 'network_type'])['value'].sum().reset_index()
sum_packets_data = packets_data.groupby(['framework', 'framework_pod', 'type', 'network_type'])['value'].sum().reset_index()

# Daten nach der Summe der Werte sortieren
sum_bytes_data['total_value'] = sum_bytes_data.groupby('framework_pod')['value'].transform('sum')
sum_packets_data['total_value'] = sum_packets_data.groupby('framework_pod')['value'].transform('sum')
sorted_sum_bytes_data = sum_bytes_data.sort_values('total_value', ascending=False)
sorted_sum_packets_data = sum_packets_data.sort_values('total_value', ascending=False)

# Funktion zum Erstellen und Speichern von Plots
def create_and_save_plot(data, title, ylabel, filename):
    plt.figure(figsize=(16, 10))
    sns.barplot(x='framework_pod', y='value', hue='type', data=data, ci=None)
    plt.title(title)
    plt.xlabel('Pod')
    plt.ylabel(ylabel)
    plt.legend(title='Type')
    plt.xticks(rotation=90)  # Drehe die x-Achsen-Beschriftungen für bessere Lesbarkeit
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Gesamte Datenplots erstellen und speichern
create_and_save_plot(sorted_sum_bytes_data, 'Total Bytes by Pod and Type for Each Framework', 'Total Bytes', 'total_bytes_all_frameworks.png')
create_and_save_plot(sorted_sum_packets_data, 'Total Packets by Pod and Type for Each Framework', 'Total Packets', 'total_packets_all_frameworks.png')

# Separate Plots für die Frameworks und Network Types erstellen und speichern
frameworks = ['Oakestra', 'OCM', 'Karmada']
network_types = ['kubernetes', 'oakestra']

for framework in frameworks:
    for network_type in network_types:
        framework_network_bytes_data = sorted_sum_bytes_data[(sorted_sum_bytes_data['framework'].str.lower() == framework.lower()) & (sorted_sum_bytes_data['network_type'] == network_type)]
        framework_network_packets_data = sorted_sum_packets_data[(sorted_sum_packets_data['framework'].str.lower() == framework.lower()) & (sorted_sum_packets_data['network_type'] == network_type)]
        
        if not framework_network_bytes_data.empty:
            create_and_save_plot(framework_network_bytes_data, f'Total Bytes by Pod and Type for {framework} Framework ({network_type})', 'Total Bytes', f'total_bytes_{framework.lower()}_{network_type}.png')
        if not framework_network_packets_data.empty:
            create_and_save_plot(framework_network_packets_data, f'Total Packets by Pod and Type for {framework} Framework ({network_type})', 'Total Packets', f'total_packets_{framework.lower()}_{network_type}.png')

print("Plots gespeichert.")
