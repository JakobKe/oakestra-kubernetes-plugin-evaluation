import os
import pandas as pd

def concatenate_csv_files(directory_path):
    # List to store all data
    all_data = []
    
    # Loop through all files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            # Path to the current file
            filepath = os.path.join(directory_path, filename)
            
            # Read the CSV file
            data = pd.read_csv(filepath)
            
            # Add the data to the list
            all_data.append(data)
    
    # Concatenate all data
    concatenated_data = pd.concat(all_data, ignore_index=True)
    
    return concatenated_data

def calculate_stats(data):
    # Calculate the median and standard deviation of CPU usage for each pod
    stats = data.groupby('pod')['value'].agg(['median', 'std']).reset_index()
    stats.columns = ['Pod', 'CPU_Usage_Median', 'CPU_Usage_StdDev']
    
    return stats

def save_stats_to_csv(stats, filename='pod_cpu_usage_stats.csv'):
    # Save the statistics to a CSV file
    stats.to_csv(filename, index=False)

def main(directory_path):
    # Concatenate the CSV files and calculate the statistics
    data = concatenate_csv_files(directory_path)
    stats = calculate_stats(data)
    
    # Save the statistics to a CSV file
    save_stats_to_csv(stats)

if __name__ == "__main__":

    
    directory_path = "oakestra"
    main(directory_path)
