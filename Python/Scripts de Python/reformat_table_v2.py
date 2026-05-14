import pandas as pd
import re
import os
import sys

input_file = '/home/jpmr/Desktop/AI test/Coisa naj/JP_tabela geral_CGEM_copia.csv'
output_dir = '/home/jpmr/Desktop/AI test/Coisa naj' # Output directly to user folder for ease

def clean_value(cell, default_ir):
    """
    Parses the cell content to extract properly formatted IR numbers.
    Removes 'x', 'ire', 'i.r.e.', parentheses, and other text.
    If 'x' is found but no number, uses default_ir.
    If default_ir is also missing, returns "Present".
    """
    if pd.isna(cell) or str(cell).strip() == '':
        return None
    
    s = str(cell).strip()
    
    # CASE 1: exact 'x' or 'X' or 'xx'
    if s.lower() == 'x' or s.lower() == 'xx':
        cleaned_default = clean_simple_number(default_ir)
        if cleaned_default:
            return cleaned_default
        return "?" # Use 'Present' or '?' to indicate presence without value
    
    # CASE 2: Text containing numbers
    # Regex to find numbers. 
    found_numbers = re.findall(r'\d+(?:\.\d+)?', s)

    # Filter out numbers that look clearly wrong (like "1" or "2" if they are just counts?)
    # But usually all found numbers here are relevant.
    
    if not found_numbers:
        # No numbers found in text (e.g., "x (ire ...)" but regex failed due to typo?)
        # Or just text.
        if 'x' in s.lower():
            cleaned_default = clean_simple_number(default_ir)
            if cleaned_default:
                return cleaned_default
            return "?" # Present
        return None

    # Clean duplicates and sort
    cleaned_list = []
    for num_str in found_numbers:
        try:
            val = float(num_str)
            cleaned_list.append(val)
        except:
            continue
            
    if not cleaned_list:
        # Fallback
        cleaned_default = clean_simple_number(default_ir)
        if cleaned_default:
            return cleaned_default
        return "?"
        
    unique_vals = sorted(list(set(cleaned_list)))
    
    # Format back to string
    str_vals = []
    for v in unique_vals:
        if v.is_integer():
            str_vals.append(str(int(v)))
        else:
            str_vals.append(str(v))
            
    return ", ".join(str_vals)

def clean_simple_number(val):
    """Helper to clean the default/literature IR value which is just a single number usually."""
    if pd.isna(val) or str(val).strip() == '':
        return ""
    # Just extract the first number found
    found = re.findall(r'\d+(?:\.\d+)?', str(val))
    if found:
        try:
            f = float(found[0])
            if f.is_integer():
                return str(int(f))
            return str(f)
        except:
            return str(val)
    return str(val)

def generate_prototypes():
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    
    non_sample_headers = ['Coluna', 'Referencia', 'DOI', 'Classe química']
    
    headers = df.columns.tolist()
    start_sample_idx = 3
    end_sample_idx = len(headers)
    
    for i in range(start_sample_idx, len(headers)):
        col_name = headers[i].strip()
        match = False
        for ns in non_sample_headers:
            if ns.lower() == col_name.lower():
                match = True
                break
        if match:
            end_sample_idx = i
            break
            
    sample_cols = headers[start_sample_idx:end_sample_idx]
    print(f"Identified {len(sample_cols)} sample columns.")
    
    # Metadata columns
    col_ref = None
    col_doi = None
    col_class = None
    col_ir_lit = headers[2]
    col_compound = headers[0]
    col_ir_exp = headers[1]
    
    for h in headers:
        hl = h.lower().strip()
        if 'referencia' in hl or 'referência' in hl:
            col_ref = h
        elif 'doi' in hl:
            col_doi = h
        elif 'classe' in hl and 'química' in hl:
            col_class = h
            
    processed_rows = []
    
    for idx, row in df.iterrows():
        compound = str(row[col_compound]).strip()
        if compound.lower() == 'nan': compound = ''
        
        chem_class = str(row[col_class]).strip() if col_class and pd.notna(row[col_class]) else ''
        if chem_class.lower() == 'nan': chem_class = ''
        
        ir_lit = clean_simple_number(row[col_ir_lit])
        
        ref = str(row[col_ref]).strip() if col_ref and pd.notna(row[col_ref]) else ''
        if ref.lower() == 'nan': ref = ''
        
        doi = str(row[col_doi]).strip() if col_doi and pd.notna(row[col_doi]) else ''
        if doi.lower() == 'nan': doi = ''
        
        default_ir = row[col_ir_exp]
        
        found_parts = []
        
        for sample in sample_cols:
            raw_cell = row[sample]
            ir_val = clean_value(raw_cell, default_ir)
            
            if ir_val:
                # If IR value is available (either number or "Present"), add it
                if ir_val != "?":
                    found_parts.append(f"{sample} ({ir_val})")
                else:
                    # If just present but no value known
                    found_parts.append(f"{sample}")
        
        if found_parts:
            found_str = " | ".join(found_parts)
            
            processed_rows.append({
                'Compound': compound,
                'Class': chem_class,
                'IR Literature': ir_lit,
                'Found In': found_str,
                'Reference': ref,
                'DOI': doi
            })
            
    df_out = pd.DataFrame(processed_rows)
    final_output_path = os.path.join(output_dir, 'prototype_3_condensed_final.csv')
    df_out.to_csv(final_output_path, index=False, sep=';', encoding='utf-8-sig') 
    print(f"Saved to {final_output_path}")

if __name__ == "__main__":
    generate_prototypes()
