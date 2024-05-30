import pandas as pd
import matplotlib.pyplot as plt

# File names and Orchestration Framework mappings
files = {
    'karmada_100_combined_average_time_intervals.csv': 'Karmada',
    'ocm_100_combined_average_time_intervals.csv': 'OCM',
    'kubernetes_yaml_100_combined_average_time_intervals.csv': 'Kubernetes',
    'oakestra_100_combined_average_time_intervals.csv': 'Oakestra',
}

# Prepare DataFrames
data_frames = []
cleanup_frames = []
total_times_frames = []

for file, label in files.items():
    df = pd.read_csv(file)
    # Set the Orchestration Framework as a column
    df['Orchestration Framework'] = label
    # Main DataFrame excluding "Delete_to_CleanUp"
    main_df = df[df['Step'] != 'Delete_to_CleanUp'][['Step', 'Average_Time', 'Orchestration Framework']]
    data_frames.append(main_df)
    # Special DataFrame only for "Delete_to_CleanUp"
    cleanup_df = df[df['Step'] == 'Delete_to_CleanUp'][['Step', 'Average_Time', 'Orchestration Framework']]
    cleanup_frames.append(cleanup_df)
    # DataFrame for Total Deployment and Deletion Time
    total_times_df = df[df['Step'].isin(['Total_Time_Deployment', 'Total_Time_Deletion'])][['Step', 'Average_Time', 'Orchestration Framework']]
    total_times_frames.append(total_times_df)

# Main DataFrame for the stacked bar chart
final_df = pd.concat(data_frames)
steps_order = [
    'Deployed_to_PodScheduled',
    'PodScheduled_to_Init',
    'Init_to_ContainersReady',
    'ContainersReady_to_Ready'
]
final_df['Step'] = pd.Categorical(final_df['Step'], categories=steps_order, ordered=True)
pivot_df = final_df.pivot_table(index='Orchestration Framework', columns='Step', values='Average_Time', aggfunc='sum')

# Special DataFrame for "Delete_to_CleanUp"
cleanup_df = pd.concat(cleanup_frames)
cleanup_pivot = cleanup_df.pivot_table(index='Orchestration Framework', columns='Step', values='Average_Time', aggfunc='sum')

# DataFrame for Total Times
total_times_df = pd.concat(total_times_frames)
total_times_pivot = total_times_df.pivot_table(index='Orchestration Framework', columns='Step', values='Average_Time', aggfunc='sum')

# First Diagram: Total time per Orchestration Framework divided by steps
fig, ax = plt.subplots(figsize=(10, 6))
pivot_df.plot(kind='bar', stacked=True, ax=ax)
plt.title('Total Time per Orchestration Framework Divided by Steps')
plt.ylabel('Time in Milliseconds')
plt.xlabel('Orchestration Framework')
plt.xticks(rotation=45)
plt.legend(title='Step')
plt.tight_layout()
plt.savefig('deployment_time_per_orchestration_framework.png')  # Save as PNG

# Second Diagram: Specialized on "Delete to CleanUp"
fig, ax = plt.subplots(figsize=(10, 6))
cleanup_pivot.plot(kind='bar', ax=ax)
plt.title('Time for "Delete to CleanUp" per Orchestration Framework')
plt.ylabel('Time in Milliseconds')
plt.xlabel('Orchestration Framework')
plt.xticks(rotation=45)
plt.legend(title='Step')
plt.tight_layout()
plt.savefig('delete_to_cleanup_time_per_orchestration_framework.png')  # Save as PNG

# Third Diagram: Total Deployment and Deletion Time
fig, ax = plt.subplots(figsize=(10, 6))
total_times_pivot.plot(kind='bar', ax=ax)
plt.title('Total Deployment and Deletion Times per Orchestration Framework')
plt.ylabel('Time in Milliseconds')
plt.xlabel('Orchestration Framework')
plt.xticks(rotation=45)
plt.legend(title='Time Type')
plt.tight_layout()
plt.savefig('total_deployment_and_deletion_time_per_orchestration_framework.png')  # Save as PNG

plt.show()
