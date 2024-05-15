import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def parse_datetime(date_str):
    try:
        return pd.to_datetime(date_str)
    except ValueError:
        # Entferne das letzte Wort (Zeitzone) und parse erneut
        date_str = ' '.join(date_str.split()[:-1])
        return pd.to_datetime(date_str)

def remove_timezone(dt):
    return dt.dt.tz_localize(None)

def plot_deployment_times(csv_file, save_dir, file_name):
    # CSV-Datei einlesen
    data = pd.read_csv(csv_file)

    # Zeitspalten in Datetime-Format umwandeln
    time_columns = ['DeploymentTime', 'Initialized', 'PodScheduled', 'ContainersReady', 'Ready', 'DeleteTime', 'TerminationTime', 'CleanUpTime']
    for col in time_columns:
        data[col] = data[col].apply(parse_datetime)

    # Zeitzoneninformationen entfernen
    for col in time_columns:
        data[col] = remove_timezone(data[col])
        
    # Zeilen mit ungültigen 'DeleteTime'-Typen entfernen
    invalid_rows = data[data['DeleteTime'].apply(lambda x: not isinstance(x, pd.Timestamp))].index
    data.drop(index=invalid_rows, inplace=True)

    # Datentypen der Spalten ausgeben
    print(data.dtypes)

  # Zeilen mit ungültigen 'DeleteTime'-Typen entfernen
    data = data.dropna(subset=['DeleteTime'])
    invalid_rows = data[data['DeleteTime'].apply(lambda x: not isinstance(x, pd.Timestamp))].index
    data.drop(index=invalid_rows, inplace=True)

    # Sicherstellen, dass alle Spalten im Datetime-Format sind
    for col in time_columns:
        if data[col].dtype != 'datetime64[ns]':
            raise TypeError(f"Column {col} is not in datetime format")

   

    # Neue Spalten für die Dauer zwischen den Zeitpunkten berechnen
    data['InitTime'] = (data['Initialized'] - data['DeploymentTime']).dt.total_seconds()
    data['SchedTime'] = (data['PodScheduled'] - data['Initialized']).dt.total_seconds()
    data['ContReadyTime'] = (data['ContainersReady'] - data['PodScheduled']).dt.total_seconds()
    data['ReadyTime'] = (data['Ready'] - data['ContainersReady']).dt.total_seconds()
    
    data['TermTime'] = (data['TerminationTime'] - data['DeleteTime']).dt.total_seconds()
    data['CleanTime'] = (data['CleanUpTime'] - data['TerminationTime']).dt.total_seconds()
    
    
    
   

    # Daten für das Plotten vorbereiten
    melt_data = data.melt(id_vars=['DeploymentName', 'PodName'], value_vars=['InitTime', 'SchedTime', 'ContReadyTime', 'ReadyTime', 'DeleteTime', 'TermTime', 'CleanTime'],
                          var_name='Phase', value_name='Duration')

    # Diagramm mit Seaborn erstellen
    plt.figure(figsize=(14, 10))
    sns.boxplot(x='Phase', y='Duration', data=melt_data)
    sns.swarmplot(x='Phase', y='Duration', data=melt_data, color='.25', size=3)

    # Diagramm anpassen
    plt.title('Zeitliche Dauer der verschiedenen Phasen der Deployments')
    plt.xlabel('Phase')
    plt.ylabel('Dauer (Sekunden)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Sicherstellen, dass der Speicherordner existiert
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Datei speichern
    file_path = os.path.join(save_dir, file_name)
    plt.savefig(file_path)
    plt.show()



# Beispielverwendung
csv_file = './../tests/deploy-undeploy/kubernetes/kubernetes.deploy.undeploy.csv'  # Pfad zur CSV-Datei angeben
save_dir = 'path_to_save_directory'  # Pfad zum Speicherordner angeben
file_name = 'deployment_times_plot.png'  # Name der zu speichernden Datei

plot_deployment_times(csv_file, save_dir, file_name)
