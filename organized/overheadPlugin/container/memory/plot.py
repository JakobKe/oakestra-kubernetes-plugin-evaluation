import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Hilfsfunktion zur Bereinigung des Pod-Namens
def clean_pod_name(pod_name):
    parts = pod_name.split('-')
    if len(parts) > 2:
        return '-'.join(parts[:-2])  # Alles nach dem vorletzten "-" entfernen
    return pod_name  # Keine Änderung, wenn weniger als zwei "-" vorhanden sind

# Reading data from the CSV file
df = pd.read_csv('total_mem_pod_plugin.csv')

# Bereinigung der Pod-Namen
df['pod'] = df['pod'].apply(clean_pod_name)

# Plot 1: Barplot showing average values per pod, grouped by framework
plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='pod', y='average_value', hue='framework')
plt.xticks(rotation=90)
plt.title('Average Values per Pod and Framework')
plt.ylabel('Average Value')
plt.xlabel('Pod')
plt.tight_layout()
plt.savefig('average_values_per_pod_and_framework.png')  # Saving the plot to a file
plt.show()

# Plot 2: Bar chart displaying the sum of average values per framework
plt.figure(figsize=(8, 6))
framework_sums = df.groupby('framework')['average_value'].sum().reset_index()
sns.barplot(data=framework_sums, x='framework', y='average_value')
plt.title('Sum of Average Values by Framework')
plt.ylabel('Sum of Average Values')
plt.xlabel('Framework')
plt.savefig('sum_of_average_values_by_framework.png')  # Saving the plot to a file
plt.show()
