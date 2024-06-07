import pandas as pd
import matplotlib.pyplot as plt

def read_csv_files(filepaths):
    # Read each CSV file and store the data in a list
    data_list = []
    for filepath in filepaths:
        data = pd.read_csv(filepath)
        data_list.append(data)
    return data_list

def calculate_sum(data_list):
    # Calculate the sum of CPU usage median values for each file
    sum_stats = []
    for data in data_list:
        total_sum = data['CPU_Usage_Median'].sum()
        sum_stats.append(total_sum)
    return sum_stats

def plot_data(sum_stats, labels):
    # Plot the sum of CPU usage values for each CSV file in a bar plot
    plt.figure(figsize=(10, 6))
    plt.bar(labels, sum_stats, color='skyblue')
    plt.xlabel('CSV File')
    plt.ylabel('Sum of CPU Usage Median')
    plt.title('Sum of CPU Usage Median by CSV File')
    plt.tight_layout()
    plt.show()

def main(filepaths):
    # Read the CSV files
    data_list = read_csv_files(filepaths)
    
    # Calculate the sum statistics
    sum_stats = calculate_sum(data_list)
    
    # Plot the sum statistics
    plot_data(sum_stats, labels=filepaths)

if __name__ == "__main__":
    # Specify the filepaths of the two CSV files
    filepaths = ['network-type-median-oakestra.kubernetes.csv', 'network-type-median-oakestra.oakestra.csv']
    
    # Call the main function
    main(filepaths)
