import os
import pandas as pd

def concatenate_csv_files(directory_paths):
    # List to store all data
    all_data = []
    
    # Loop through all provided directories
    for directory in directory_paths:
        # Loop through all files in the current directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                # Path to the current file
                filepath = os.path.join(directory, filename)
                
                # Read the CSV file
                data = pd.read_csv(filepath)
                
                # Add the framework name
                data['framework'] = os.path.basename(directory)
                
                # Add the data to the list
                all_data.append(data)
    
    # Concatenate all data
    concatenated_data = pd.concat(all_data, ignore_index=True)
    
    return concatenated_data

def calculate_stats(data):
    # Calculate median and variance of CPU usage for each pod and framework
    stats = data.groupby(['framework', 'pod'])['value'].agg(['median', 'std']).reset_index()
    stats.columns = ['Framework', 'Pod', 'CPU_Usage_Median', 'CPU_Usage_StdDev']
    
    # Filter data for pods containing "overhead" or "server" in their names
    filtered_data = data[data['pod'].str.contains('overhead|server', case=False)]
    
    # Group filtered data by framework and aggregate
    filtered_stats = filtered_data.groupby('framework')['value'].agg(['median', 'std']).reset_index()
    filtered_stats['Pod'] = 'overhead-server'
    filtered_stats.columns = ['Framework', 'Filtered_CPU_Usage_Median', 'Filtered_CPU_Usage_StdDev', 'Pod']
    
    return stats, filtered_stats

def save_stats_to_csv(stats, filtered_stats, filename='pod_cpu_usage_of_component.csv'):
    # Remove original "overhead" and "server" pods from the stats
    stats = stats[~stats['Pod'].str.contains('overhead|server', case=False)]
    
    # Combine stats and filtered_stats
    final_stats = pd.concat([stats, filtered_stats], ignore_index=True)
    
    # Save the statistics data to a CSV file
    final_stats.to_csv(filename, index=False)

# List of directory paths
directories = ['oakestra', 'kubernetes', 'ocm', 'karmada']

# Concatenate the CSV files and calculate the statistics
data = concatenate_csv_files(directories)
stats, filtered_stats = calculate_stats(data)

# Save the statistics to a CSV file
save_stats_to_csv(stats, filtered_stats)
