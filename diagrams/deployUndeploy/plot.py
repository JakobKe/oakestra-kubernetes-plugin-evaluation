import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Liste der CSV-Dateien

csv_files = [
    'average_time_intervals.csv',
    'average_time_intervals.csv',
    'average_time_intervals.csv'
]


all_data = pd.DataFrame()

for i, file in enumerate(csv_files):
    df = pd.read_csv(file)
    df['Deployment'] = f'Deployment {i + 1}' 
    all_data = pd.concat([all_data, df], ignore_index=True)


all_data['Total_Time'] = all_data.groupby('Deployment')['Average_Time'].transform('sum')


plot_data = all_data.pivot(index='Deployment', columns='Step', values='Average_Time')

plot_data.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='tab10')

plt.xlabel("")
plt.ylabel("Time (ms)")
plt.title("Deployment Steps")
plt.legend(title="Steps")
plt.ylim(0, 10000)
plt.tight_layout()

plt.savefig('images/deployment_steps.png')

plt.show()