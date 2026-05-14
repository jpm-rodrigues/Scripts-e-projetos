import pandas as pd
import re
import os

input_file = '/home/jpmr/Desktop/AI test/Coisa naj/JP_tabela geral_CGEM_copia.csv'
output_dir = '/home/jpmr/.gemini/antigravity/brain/b7058901-316a-4b26-992e-9c1175d04056'

def clean_value(cell, default_ir):
    """Parses the cell content to extract the IR value."""
    if pd.isna(cell) or str(cell).strip() == '':
        return None
    
    s = str(cell).strip()
    
    # Simple 'x' -> use default IR
    if s.lower() == 'x':
        return default_ir
    
    # Try to find numbers in the string
    numbers = re.findall(r'\d+(?:[.,]\d+)?', s)
    
    if not numbers:
        return default_ir
    
    # If numbers found, join them
    unique_numbers = sorted(list(set(numbers)))
    return ", ".join(unique_numbers)

def generate_prototypes():
    df = pd.read_csv(input_file)
    
    # Identify columns
    non_sample_cols_end = ['Coluna', 'Referencia', 'DOI', 'Classe química']
    
    sample_cols = []
    # Start checking from column index 3 (after COMPOUNDS, IR exp, IR lit)
    for col in df.columns[3:]:
        if col in non_sample_cols_end:
            break
        sample_cols.append(col)
        
    print(f"Identified {len(sample_cols)} sample columns.")
    
    # --- Prototype 3: Condensed List ---
    # Compound | Class | IR Lit | Found In | Reference | DOI
    condensed_rows = []
    for idx, row in df.iterrows():
        compound = row['COMPOUNDS']
        chem_class = row['Classe química'] if 'Classe química' in df.columns else ''
        ir_lit = row['IR literature']
        nm_ref = row['Referencia'] if 'Referencia' in df.columns else ''
        doi_ref = row['DOI'] if 'DOI' in df.columns else ''
        
        found_in = []
        default_ir = row['IR experimental']
        
        for sample in sample_cols:
            raw_val = row[sample]
            cleaned = clean_value(raw_val, default_ir)
            if cleaned:
                # Format: Sample (IR)
                found_in.append(f"{sample} ({cleaned})")
        
        if found_in:
            condensed_rows.append({
                'Compound': compound,
                'Class': chem_class,
                'IR Literature': ir_lit,
                'Found In': " | ".join(found_in),
                'Reference': nm_ref,
                'DOI': doi_ref
            })
            
    df_condensed = pd.DataFrame(condensed_rows)
    # Using semicolon separator which is standard for CSVs in regions using comma decimals (like Brazil)
    # This ensures LibreOffice opens it correctly without user parsing dialogs for most defaults.
    df_condensed.to_csv(os.path.join(output_dir, 'prototype_3_condensed.csv'), index=False, sep=';')
    
    print("Prototype 3 generated successfully with separator fixes.")

if __name__ == "__main__":
    generate_prototypes()
