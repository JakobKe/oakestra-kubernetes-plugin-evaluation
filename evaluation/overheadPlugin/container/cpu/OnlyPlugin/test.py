import pandas as pd

# Daten aus der CSV-Datei einlesen
data = pd.read_csv('/Users/jakobkempter/Desktop/oakestra-kubernetes-plugin-evaluation/organized/overheadPlugin/container/cpu/OnlyPlugin/oakestra/3_container_cpu_usage_seconds_total--pods:.*.csv')

# Berechne den Durchschnitt und die Varianz der CPU-Auslastung für jeden Pod
stats = data.groupby('pod')['value'].agg(['mean', 'std']).reset_index()
stats['coefficient_of_variation'] = (stats['std'] / stats['mean']) * 100

# Speichere die Statistik-Daten in einer CSV-Datei
stats.to_csv('pod_memory_stats.csv', index=False)

print(stats)
