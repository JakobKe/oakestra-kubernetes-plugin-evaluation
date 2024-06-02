import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Read data from a CSV file
data = pd.read_csv('average_cpu_total_usage.csv')

# Check the first few rows and data types
print(data.head())
print(data.dtypes)

# Create a bar plot
plt.figure(figsize=(10, 6))  # Adjust the size of the plot
bar_plot = sns.barplot(x='framework', y='average_cpu_total', data=data, ci=None)

# Add title and labels
plt.title('Average CPU Usage by Framework')
plt.xlabel('Framework')
plt.ylabel('Average CPU Usage')

# Set limits for the y-axis
plt.ylim(23.75, 23.95)  # Set the y-axis limits

# Finer tick intervals on the y-axis
plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(0.01))  # Set major ticks every 0.01 units
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.005))  # Set minor ticks every 0.005 units

plt.savefig('cpu_usage_plot.png')

# Display the plot
plt.show()


