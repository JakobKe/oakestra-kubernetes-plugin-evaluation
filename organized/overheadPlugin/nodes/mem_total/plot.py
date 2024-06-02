import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Daten aus einer CSV-Datei einlesen
data = pd.read_csv('total_mem_usage.csv')

# Umwandeln von Bytes in Gigabytes
data['Total Mem Usage All Nodes'] = data['Total Mem Usage All Nodes'] / (1024**3)

# Balkendiagramm erstellen
plt.figure(figsize=(10, 6))  # Größe des Diagramms anpassen
bar_plot = sns.barplot(x='framework', y='Total Mem Usage All Nodes', data=data)

# Titel und Labels hinzufügen
plt.title('Total Memory Usage by Framework (in Gigabytes)')
plt.xlabel('Framework')
plt.ylabel('Total Memory Usage (GB)')

# Verbesserung der y-Achse für bessere Lesbarkeit
plt.gca().set_ylim(bottom=0)  # Startet die y-Achse bei 0 für bessere Vergleichbarkeit


plt.savefig('memory_usage_plot.png')

# Diagramm anzeigen
plt.show()
