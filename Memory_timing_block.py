import argparse 
import pandas as pd
import os
import subprocess 

# Set up argparse to take input file from the command line
parser = argparse.ArgumentParser(description='Generate timing files from an Excel input file.')
parser.add_argument('input_file', type=str, help='Path to the input Excel (.xlsx) file')
args = parser.parse_args()

# Get input file path
input_file = args.input_file

# Auto-detect run and phase from filename
filename = os.path.basename(input_file)  # e.g., 'Run1_Recognition.xlsx'
basename = filename.replace('.xlsx', '')

# Extract run and phase
parts = basename.split('_')
run = parts[0]        # 'Run1'
phase_raw = parts[1]  # 'Recognition'
phase = 'Recog' if 'recog' in phase_raw.lower() else 'Study'

df = pd.read_excel(input_file)
# Preprocessing: fill NA to ensure no crashes
df['Condition'] = df['Condition'].fillna('FALSE')

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'Memory Block timing files')
os.makedirs(output_dir, exist_ok=True)

#Material Type identifiers
material_types = {
    'Object': 'Obj',
    'Scene': 'Scene',
    'Pair': 'Pair'
}


# Helper function to process blocks and write files
def process_material(df_material, material_label):
    output_rows = []
    current_block_start = None
    current_block_start_onset = None

    for idx, row in df_material.iterrows():
        if current_block_start is None:
            current_block_start = idx
            current_block_start_onset = row['Onset_Time']

        if str(row['Condition']) == 'FALSE':
            # End the block at the previous row
            last_row = df_material.loc[idx - 1]
            end_time = last_row['Onset_Time'] + last_row['Duration']
            duration = end_time - current_block_start_onset
            output_rows.append((current_block_start_onset, duration, 1))
            current_block_start = None
            current_block_start_onset = None

    # Save to txt file
    output_filename = f'{phase}_{run}_{material_label}.txt'
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as f:
        for onset, dur, mod in output_rows:
            f.write(f"{onset:.6f}\t{dur:.6f}\t{mod}\n")

# Process each material type separately
for mat_type, mat_label in material_types.items():
    df_mat = df[df['Material_T'] == mat_type]
    if not df_mat.empty:
        process_material(df_mat, mat_label)

print(f"Timing files created in {output_dir}")
subprocess.run(["open", output_dir])
