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

# Ändere die Reihenfolge der Schritte für den letzten Plot
total_times_pivot = total_times_df.pivot_table(index='Orchestration Framework', columns='Step', values='Average_Time', aggfunc='sum')
total_times_pivot = total_times_pivot[['Total_Time_Deployment', 'Total_Time_Deletion']]

framework_colors = {
    'oakestra': '#666f21',  # Grün
    'ocm': '#ffc000',       # Orange
    'karmada': '#bf4129'    # Blau
}

# Farbpaletten als Hex-Codes definieren
palette_deployment = ['#666f21', '#ffc000', '#bf4129', '#6F2166']
palette_cleanup = ['#21666F']
palette_total_times = ['#666f21', '#21666F']

# Funktion zum Erstellen und Speichern von Plots mit benutzerdefinierter Farbpalette
def create_and_save_plot(pivot_df, ylabel, filename, palette):
    pivot_df.columns = pivot_df.columns.str.replace('_', ' ')
    print(pivot_df)
    plt.rcParams.update({'font.size': 14})
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_df.plot(kind='bar', stacked=True, ax=ax, color=palette)
    plt.ylabel(ylabel, fontsize=16)
    plt.xlabel('Framework', fontsize=16)
    plt.xticks(rotation=45)
    plt.legend(title='Step')
    plt.tight_layout()
    plt.savefig(filename)  # Save as PNG
    plt.show()
    plt.close()

# Funktion zum Erstellen und Speichern des Total Time Plots
def create_and_save_total_times_plot(pivot_df, ylabel, filename, palette):
    pivot_df.columns = pivot_df.columns.str.replace('_', ' ')
    print(pivot_df)
    plt.rcParams.update({'font.size': 14})
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_df.plot(kind='bar', stacked=True, ax=ax, color=palette)
    plt.ylabel(ylabel, fontsize=16)
    plt.xlabel('Framework', fontsize=16)
    plt.xticks(rotation=45)
    plt.legend(title='Step')
    plt.tight_layout()
    plt.savefig(filename)  # Save as PNG
    plt.show()
    plt.close()

# First Diagram: Total time per Orchestration Framework divided by steps
create_and_save_plot(pivot_df, 'Time in Milliseconds', 'deployment_time_per_orchestration_framework.png', palette_deployment)

# Second Diagram: Specialized on "Delete to CleanUp"
create_and_save_plot(cleanup_pivot, 'Time in Milliseconds', 'delete_to_cleanup_time_per_orchestration_framework.png', palette_cleanup)

# Third Diagram: Total Deployment and Deletion Time
create_and_save_total_times_plot(total_times_pivot, 'Time in Milliseconds', 'total_deployment_and_deletion_time_per_orchestration_framework.png', palette_total_times)

print("Die Plots wurden gespeichert.")
