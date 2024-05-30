import pandas as pd
import os

# Funktion zum Konvertieren von Zeitstempeln in Millisekunden
def convert_to_milliseconds(time_str):
    time_str = time_str.replace(' +0200 CEST', '+02:00')
    dt = pd.to_datetime(time_str)
    epoch = pd.Timestamp("1970-01-01", tz=dt.tz)
    return (dt - epoch).total_seconds() * 1000

# Verzeichnis mit CSV-Dateien
directory_base_path = './../../results/deploymentTime/'
csv_dir = 'kubernetes/client/100'
directory_path = directory_base_path + csv_dir

# Liste zur Speicherung der DataFrames
dataframes = []
total_deployment_times = []
total_deletion_times = []

# Durchlaufen aller CSV-Dateien im Verzeichnis
for file_name in os.listdir(directory_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(directory_path, file_name)
        df = pd.read_csv(file_path)
        
        # Konvertieren der Zeitstempel in Millisekunden
        for col in ['DeploymentTime', 'PodScheduled', 'Initialized', 'ContainersReady', 'Ready', 'DeleteTime', 'CleanUpTime']:
            df[col] = df[col].apply(convert_to_milliseconds)

        # Berechnen der Abstände zwischen den Spalten in Millisekunden
        df['Deployed_to_PodScheduled'] = df['PodScheduled'] - df['DeploymentTime']
        df['PodScheduled_to_Init'] = df['Initialized'] - df['PodScheduled']
        df['Init_to_ContainersReady'] = df['ContainersReady'] - df['Initialized']
        df['ContainersReady_to_Ready'] = df['Ready'] - df['ContainersReady']
        df['Delete_to_CleanUp'] = df['CleanUpTime'] - df['DeleteTime']

        # Berechnung der Gesamtzeiten für den gesamten Testlauf
        total_deployment_time = df['Ready'].max() - df['DeploymentTime'].min()
        total_deletion_time = df['CleanUpTime'].max() - df['DeleteTime'].min()
        total_deployment_times.append(total_deployment_time)
        total_deletion_times.append(total_deletion_time)

        # Auswahl der benötigten Spalten für das Ergebnis
        result_df = df[['DeploymentName', 'PodName', 'Deployed_to_PodScheduled', 'PodScheduled_to_Init', 'Init_to_ContainersReady', 'ContainersReady_to_Ready', 'Delete_to_CleanUp']]
        dataframes.append(result_df)

# Zusammenführen aller DataFrames zu einem
combined_df = pd.concat(dataframes)

# Speichern des neuen DataFrames als CSV
combined_df.to_csv('combined_time_intervals.csv', index=False)

# Durchschnitt der Gesamtzeiten für Deployment und Deletion
average_total_deployment_time = pd.Series(total_deployment_times).mean()
average_total_deletion_time = pd.Series(total_deletion_times).mean()

# Hinzufügen dieser Durchschnittswerte zum DataFrame der Durchschnittswerte
average_values = combined_df[['Deployed_to_PodScheduled', 'PodScheduled_to_Init', 'Init_to_ContainersReady', 'ContainersReady_to_Ready', 'Delete_to_CleanUp']].mean()
average_values['Total_Time_Deployment'] = average_total_deployment_time
average_values['Total_Time_Deletion'] = average_total_deletion_time

# Erstellen eines neuen DataFrames mit den Durchschnittswerten
average_df = pd.DataFrame(average_values).reset_index()
average_df.columns = ['Step', 'Average_Time']

# Speichern des neuen DataFrames als CSV
csv_name = csv_dir.replace("/", "_") + '_combined_average_time_intervals.csv'
average_df.to_csv(csv_name, index=False)

print("Die Durchschnittswerte wurden als " + csv_name + " gespeichert.")
