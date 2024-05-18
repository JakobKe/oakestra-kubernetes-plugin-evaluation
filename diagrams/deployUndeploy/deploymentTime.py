import pandas as pd

# Funktion zum Konvertieren von Zeitstempeln in Millisekunden
def convert_to_milliseconds(time_str):
    # Entfernen von nicht standardisierten Zeitzoneninformationen und Ersetzen durch '+02:00'
    time_str = time_str.replace(' +0200 CEST', '+02:00')
    dt = pd.to_datetime(time_str)
    epoch = pd.Timestamp("1970-01-01", tz=dt.tz)
    return (dt - epoch).total_seconds() * 1000

# Lesen der CSV-Datei
file_path = './../../tests/deploy-undeploy/kubernetes/kubernetes.deploy.undeploy.csv'
df = pd.read_csv(file_path)

# Konvertieren der Zeitstempel in Millisekunden
df['DeploymentTime'] = df['DeploymentTime'].apply(convert_to_milliseconds)
df['PodScheduled'] = df['PodScheduled'].apply(convert_to_milliseconds)
df['Initialized'] = df['Initialized'].apply(convert_to_milliseconds)
df['ContainersReady'] = df['ContainersReady'].apply(convert_to_milliseconds)
df['Ready'] = df['Ready'].apply(convert_to_milliseconds)
df['DeleteTime'] = df['DeleteTime'].apply(convert_to_milliseconds)
df['CleanUpTime'] = df['CleanUpTime'].apply(convert_to_milliseconds)

# Berechnen der Abstände zwischen den Spalten in Millisekunden
df['Deployed_to_PodScheduled'] = df['PodScheduled'] - df['DeploymentTime']
df['PodScheduled_to_Init'] = df['Initialized'] - df['PodScheduled']
df['Init_to_ContainersReady'] = df['ContainersReady'] - df['Initialized']
df['ContainersReady_to_Ready'] = df['Ready'] - df['ContainersReady']

df['Delete_to_CleanUp'] = df['CleanUpTime'] - df['DeleteTime']

# Erstellen eines neuen DataFrames mit den Abständen
result_df = df[['DeploymentName', 'PodName', 'Deployed_to_PodScheduled', 'PodScheduled_to_Init', 'Init_to_ContainersReady', 'ContainersReady_to_Ready', 'Delete_to_CleanUp']]

# Speichern des neuen DataFrames als CSV
result_df.to_csv('time_intervals.csv', index=False)

# Berechnen der Durchschnittswerte für jeden Schritt
average_values = result_df[['Deployed_to_PodScheduled', 'PodScheduled_to_Init', 'Init_to_ContainersReady', 'ContainersReady_to_Ready', 'Delete_to_CleanUp']].mean()

# Erstellen eines neuen DataFrames mit den Durchschnittswerten
average_df = pd.DataFrame(average_values, columns=['Average_Time']).reset_index()
average_df.columns = ['Step', 'Average_Time']

# Speichern des neuen DataFrames als CSV
average_df.to_csv('average_time_intervals.csv', index=False)

print("Das neue CSV wurde als 'time_intervals.csv' gespeichert.")
print("Die Durchschnittswerte wurden als 'average_time_intervals.csv' gespeichert.")
