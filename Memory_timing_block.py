import argparse 
import pandas as pd
import os
import subprocess 

# Set up argparse to take input file from the command line
parser = argparse.ArgumentParser(description='Generate recognition timing files from a folder of Excel sheets.')
parser.add_argument('input_folder', type=str, help='Path to folder with recognition .xlsx files')
args = parser.parse_args()
input_folder = args.input_folder

# Output folder
output_dir = os.path.join(os.path.dirname(__file__), 'Memory Block timing files')
os.makedirs(output_dir, exist_ok=True)

#Material Type identifiers
material_types = {
    'Object': 'Obj',
    'Scene': 'Scene',
    'Pair': 'Pair'
}

excel_files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]

for file in excel_files:
    if 'recognition' not in file.lower():
        continue  # Skip non-recognition files

    input_file = os.path.join(input_folder, file)
    filename = os.path.basename(input_file)
    basename = filename.replace('.xlsx', '')
    parts = basename.split('_')

    if len(parts) < 2:
        print(f"Skipping improperly named file: {filename}")
        continue

    run = parts[0]  # Run1, Run2, etc.
    phase = 'Recog'

    df = pd.read_excel(input_file)
    df['Condition'] = df['Condition'].fillna('FALSE')

    def process_material(df_material, material_label):
        output_rows = []
        current_block_start = None
        current_block_start_onset = None

        for idx, row in df_material.iterrows():
            if current_block_start is None:
                current_block_start = idx
                current_block_start_onset = row['Onset_Time']

            if str(row['Condition']) == 'FALSE':
                last_row = df_material.loc[idx - 1]
                end_time = last_row['Onset_Time'] + last_row['Duration']
                duration = end_time - current_block_start_onset
                output_rows.append((current_block_start_onset, duration, 1))
                current_block_start = None
                current_block_start_onset = None

        output_filename = f'{phase}_{run}_{material_label}.txt'
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w') as f:
            for onset, dur, mod in output_rows:
                f.write(f"{onset:.6f}\t{dur:.6f}\t{mod}\n")

    for mat_type, mat_label in material_types.items():
        df_mat = df[df['Material_T'] == mat_type]
        if not df_mat.empty:
            process_material(df_mat, mat_label)

# Open the output folder on macOS automatically
subprocess.run(["open", output_dir])

print(f"\n Timing files saved to: {output_dir}")
