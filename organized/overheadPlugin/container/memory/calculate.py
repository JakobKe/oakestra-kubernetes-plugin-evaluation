import pandas as pd
import os

def custom_pod_grouping(pod_name):
    # Alle Pods, die mit "oakestra-agent-" beginnen, werden zu "oakestra-agent" zusammengefasst
    if pod_name.startswith('oakestra-agent-'):
        return 'oakestra-agent'
    else:
        return pod_name

def calculate_averages(folder_path):
    # Erstellen einer Liste aller CSV-Dateien im angegebenen Ordner
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    all_averages = []

    # Durchlaufen aller Dateien und Berechnung des Durchschnittswerts für jeden Pod, wenn die Spalte 'pod' vorhanden ist
    for file in files:
        file_path = os.path.join(folder_path, file)
        data = pd.read_csv(file_path)
        
        # Überprüfung, ob die Spalte 'pod' existiert
        if 'pod' in data.columns:
            # Anwendung der Gruppierungsfunktion
            data['pod'] = data['pod'].apply(custom_pod_grouping)
            averages = data.groupby('pod')['value'].mean().reset_index()
            averages.set_index('pod', inplace=True)
            all_averages.append(averages)
        else:
            print(f"Die Datei {file} aus {folder_path} enthält keine 'pod'-Spalte und wird übersprungen.")

    # Kombinieren aller Durchschnittstabellen und Berechnung des Gesamtdurchschnitts für jeden Pod
    if all_averages:
        combined_averages = pd.concat(all_averages, axis=1)
        overall_averages = combined_averages.mean(axis=1).reset_index()
        overall_averages.columns = ['pod', 'average_value']
        overall_averages['framework'] = os.path.basename(folder_path)  # Hinzufügen des Ordnernamens als zusätzliche Spalte
        return overall_averages
    else:
        return pd.DataFrame()  # Rückgabe eines leeren DataFrame, wenn keine passenden Dateien gefunden werden

def main(folder_paths):
    all_data = []

    # Durchlaufen aller angegebenen Ordner und Aggregieren der Daten
    for folder_path in folder_paths:
        folder_averages = calculate_averages(folder_path)
        if not folder_averages.empty:
            all_data.append(folder_averages)

    # Zusammenführen aller Daten aus den verschiedenen Ordnern in eine CSV-Datei
    if all_data:
        final_data = pd.concat(all_data)
        final_data.to_csv('total_mem_pod_plugin.csv', index=False)
        print("Gesamtdurchschnittswerte wurden in 'gesamtdurchschnitt_aller_ordner.csv' gespeichert.")
    else:
        print("Keine passenden Daten gefunden. Keine Datei wurde gespeichert.")

if __name__ == "__main__":
    # Liste der Pfade zu den Ordnern
    folder_paths = ['oakestra', 'ocm', 'karmada']  # Ersetze diese Pfade mit den tatsächlichen Pfaden
    main(folder_paths)
