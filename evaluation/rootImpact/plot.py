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

# Farbpalette definieren
cpu_color = '#666f21'  # Beispiel-Hex-Code für CPU
mem_color = '#21666F'  # Beispiel-Hex-Code für Memory

# Variablen für die Anpassung der Schriftgröße
label_font_size = 20
title_font_size = 'x-large'

# Plot für CPU Usage
plt.figure(figsize=(8, 6))
sns.barplot(x='Szenario', y='Wert', data=df_cpu, color=cpu_color)
plt.ylabel('Percentage', fontsize=label_font_size)
plt.ylim(1.4, 1.9)
plt.xticks(fontsize= 20)
plt.yticks(np.arange(1.4, 1.9, 0.05), fontsize=20)

plt.xlabel('Szenario', fontsize=label_font_size)
plt.tight_layout()
plt.savefig('cpu_usage_plot.png')
plt.show()

# Plot für Memory Usage
plt.figure(figsize=(8, 6))
sns.barplot(x='Szenario', y='Wert', data=df_mem, color=mem_color)
plt.ylabel('GiB', fontsize=label_font_size)
plt.ylim(1.4, 1.6)
plt.xticks(fontsize= 20)
plt.yticks(np.arange(1.4, 1.6, 0.02), fontsize=20)
plt.xlabel('Szenario', fontsize=label_font_size)
plt.tight_layout()
plt.savefig('mem_usage_plot.png')
plt.show()
