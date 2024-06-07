import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def read_csv_files_from_directory(directory):
    """Read all CSV files from a directory and combine them into a DataFrame, ignoring the first 100 oldest timestamps in each file."""
    all_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    df_list = []
    
    for file in all_files:
        df = pd.read_csv(file)
        # Sort the dataframe by timestamp
        df = df.sort_values(by='timestamp')
        # Find the first 100 oldest timestamps in each file
        first_100_timestamps = df['timestamp'].unique()[:1]
        # Filter out the first 100 oldest timestamps
        df = df[~df['timestamp'].isin(first_100_timestamps)]
        df_list.append(df)
    
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df


def get_framework_stats(directories):
    """Read CSV files from directories and compute statistics for each framework."""
    framework_stats = []
    
    for directory in directories:
        framework_name = os.path.basename(directory)
        df = read_csv_files_from_directory(directory)
        
        # Aggregate CPU usage per timestamp
        aggregated_df = df.groupby('timestamp')['value'].sum().reset_index()
        
        print(len(aggregated_df))
        
        # Compute mean and variance
        mean_value = aggregated_df['value'].mean()
        variance = aggregated_df['value'].var()
        framework_stats.append({'framework': framework_name, 'mean': mean_value, 'variance': variance})
        
        print(directory)
        print(aggregated_df.head(5))
    
    return pd.DataFrame(framework_stats)

# Directories of the frameworks
directories = ['karmada', 'oakestra', 'ocm', 'kubernetes']  # Replace these with the actual paths

# Compute statistics for each framework
framework_stats = get_framework_stats(directories)

# Create a bar plot with Seaborn
plt.figure(figsize=(12, 6))
sns.barplot(data=framework_stats, x='framework', y='mean')
plt.errorbar(x=range(len(framework_stats)), y=framework_stats['mean'], yerr=framework_stats['variance'], fmt='none', c='red', capsize=5)
plt.xlabel('Framework')
plt.ylabel('Mean CPU Usage')
plt.title('Mean CPU Usage and Variance per Framework')
plt.xticks(rotation=45)

# Save the plot
plt.savefig('framework_cpu_mean_var.png')

# Show the plot
plt.show()

# Print the statistics
print(framework_stats)
