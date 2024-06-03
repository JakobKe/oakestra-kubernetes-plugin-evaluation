import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Laden der Daten aus einer CSV-Datei
data = pd.read_csv('average_values_per_pod.csv')

# Auswahl nur der Zeilen, die zum Framework 'oakestra' gehören und den Pod 'node-netmanager-*'
df = data[(data['framework'] == 'oakestra') & (data['pod'].str.startswith('node-netmanager'))]

# Erstellen von separaten DataFrames für Bytes und Packets
bytes_df = df[df['type'].isin(['received_bytes', 'transmit_bytes'])]
packets_df = df[df['type'].isin(['received_packets', 'transmit_packets'])]

# Gruppieren der Daten nach Network Type und Summierung der Werte
bytes_summary = bytes_df.groupby('network_type').sum().reset_index()
packets_summary = packets_df.groupby('network_type').sum().reset_index()

# Plot für Bytes spezifisch für den Pod 'node-netmanager'
plt.figure(figsize=(12, 6))
bytes_pod_plot = sns.barplot(x='network_type', y='value', data=bytes_summary)
plt.title('Sum of Bytes Transmitted and Received by Network Type for Pod node-netmanager')
plt.ylabel('Total Bytes')
plt.xlabel('Network Type')
bytes_pod_plot.figure.savefig('network_oakestra_bytes_node_netmanager.png')  # Speichern der Grafik
plt.show()

# Plot für Packets spezifisch für den Pod 'node-netmanager'
plt.figure(figsize=(12, 6))
packets_pod_plot = sns.barplot(x='network_type', y='value', data=packets_summary)
plt.title('Sum of Packets Transmitted and Received by Network Type for Pod node-netmanager')
plt.ylabel('Total Packets')
plt.xlabel('Network Type')
packets_pod_plot.figure.savefig('network_oakestra_packets_node_netmanager.png')  # Speichern der Grafik
plt.show()
