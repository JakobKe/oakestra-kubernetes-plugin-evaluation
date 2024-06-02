import os
import pandas as pd

def calculate_average_value(directory):
    # Liste zum Speichern aller Werte
    all_values = []
    
    # Durchlaufe alle Dateien im angegebenen Verzeichnis
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            # Pfad zur aktuellen Datei
            filepath = os.path.join(directory, filename)
            
            # Lese die CSV-Datei ein
            data = pd.read_csv(filepath)
            
            # Füge die Werte der Spalte 'value' zur Liste hinzu
            all_values.extend(data['value'])
    
    # Berechne den Durchschnittswert, wenn die Liste nicht leer ist
    if all_values:
        average_value = sum(all_values) / len(all_values)
        return average_value
    else:
        return "Keine Werte gefunden"

def save_averages_to_csv(directory_paths):
    # Liste zur Speicherung der Ergebnisse
    results = []

    # Gehe durch alle übergebenen Verzeichnisse
    for directory in directory_paths:
        average = calculate_average_value(directory)
        # Füge das Verzeichnis und den Durchschnittswert der Liste hinzu
        results.append({"framework": os.path.basename(directory), "average_cpu_total": average})

    # Erstelle einen DataFrame aus den Ergebnissen
    results_df = pd.DataFrame(results)
    
    # Speichere den DataFrame in einer CSV-Datei
    results_df.to_csv('average_cpu_total_usage.csv', index=False)

# Liste der Verzeichnispfade
directories = ['./ocm', './karmada', './oakestra', './kubernetes']
save_averages_to_csv(directories)
