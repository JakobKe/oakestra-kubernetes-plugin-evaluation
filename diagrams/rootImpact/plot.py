import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Daten vorbereiten
data = {
    'Szenario': ['3k', '2k1o', '1k2o', '3o'] * 2,
    'Type': ['CPU', 'CPU', 'CPU', 'CPU', 'MEM', 'MEM', 'MEM', 'MEM'],
    'Wert': [1.8347, 1.8194, 1.8376, 1.8088, 1.50, 1.53, 1.50, 1.50]
}

# DataFrame erstellen
df = pd.DataFrame(data)

# Daten für CPU und MEM trennen
df_cpu = df[df['Type'] == 'CPU']
df_mem = df[df['Type'] == 'MEM']

# Diagramm erstellen
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)  # 1 Zeile, 2 Spalten, 1. Subplot
sns.barplot(x='Szenario', y='Wert', data=df_cpu, color='blue')
plt.title('Percentage CPU Usage')
plt.ylabel('Percentage')
plt.ylim(1.4, 1.9)
plt.yticks(np.arange(1.4, 1.9, 0.05))

plt.subplot(1, 2, 2)  # 1 Zeile, 2 Spalten, 2. Subplot
sns.barplot(x='Szenario', y='Wert', data=df_mem, color='green')
plt.title('Memory Usage in GiB')
plt.ylabel('GiB')
plt.ylim(1.4, 1.6)
plt.yticks(np.arange(1.4, 1.6, 0.02))

# Anpassungen für das Layout
plt.tight_layout()

# Diagramme als PNG-Datei speichern
plt.savefig('cpu_mem_usage_plot.png')

# Diagramme anzeigen
plt.show()
