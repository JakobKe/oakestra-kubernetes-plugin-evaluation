import pandas as pd
import os
import glob

def summarize_pods(directories, output_file):
    all_data = pd.DataFrame()

    for directory in directories:
        framework_name = os.path.basename(directory)
        all_files = glob.glob(os.path.join(directory, "*.csv"))

        for file in all_files:
            df = pd.read_csv(file)
            df['framework'] = framework_name
            all_data = pd.concat([all_data, df], ignore_index=True)

    # Median und Standardabweichung für jeden Pod und Framework berechnen
    summary = all_data.groupby(['framework', 'namespace', 'pod'])['value'].agg(['median', 'std']).reset_index()

    # Neue CSV-Datei speichern
    summary.to_csv(output_file, index=False)

    print(f"Summary saved to {output_file}")
    print(summary)

# Verzeichnisse mit den CSV-Dateien angeben
directories = [
    'karmada',
    'oakestra',
    'ocm',
    'kubernetes',
    'oakestra-kubernetes'
]

# Ausgabedatei angeben
output_file = 'combined_summary_output.csv'

# Zusammenfassung erstellen und speichern
summarize_pods(directories, output_file)
