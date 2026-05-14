import pandas as pd
import re
import os
import sys
import csv

input_file = '/home/jpmr/Desktop/AI test/Coisa naj/JP_tabela geral_CGEM_copia.csv'
output_dir = '/home/jpmr/Desktop/AI test/Coisa naj'

def clean_value(cell, default_ir):
    """
    Cleans cell data to extract IR numbers or indicate presence.
    Returns string "Value" or "Value1, Value2" or "Present" (if x but no value).
    """
    if pd.isna(cell) or str(cell).strip() == '':
        return None
    
    s = str(cell).strip()
    
    # 1. Check for explicit 'x' markers
    is_present_marker = False
    if s.lower() == 'x' or s.lower() == 'xx':
        is_present_marker = True
    elif 'x' in s.lower(): 
        # 'x (ire 1234)' type strings
        is_present_marker = True
        
    # 2. Extract numbers
    # Regex for integer or decimal numbers
    found_numbers = re.findall(r'\d+(?:\.\d+)?', s)
    
    # Filter numbers? 
    # Sometimes years like "2009" in references might bleed in if logic was wrong,
    # but here we are processing SAMPLE columns only, so numbers are likely IRs.
    
    cleaned_list = []
    for num_str in found_numbers:
        try:
            val = float(num_str)
            cleaned_list.append(val)
        except:
            continue
            
    # 3. Decision Logic
    if cleaned_list:
        # We found explicit numbers in the cell
        unique_vals = sorted(list(set(cleaned_list)))
        str_vals = []
        for v in unique_vals:
            if v.is_integer():
                str_vals.append(str(int(v)))
            else:
                str_vals.append(str(v))
        return ", ".join(str_vals)
    
    elif is_present_marker:
        # Cell implies presence, but no local number found.
        # Fallback to default IR
        clean_default = clean_simple_number(default_ir)
        if clean_default:
            return clean_default
        else:
            return "Present" # No numeric value known
            
    return None

def clean_simple_number(val):
    if pd.isna(val) or str(val).strip() == '':
        return ""
    found = re.findall(r'\d+(?:\.\d+)?', str(val))
    if found:
        try:
            f = float(found[0])
            if f.is_integer():
                return str(int(f))
            return str(f)
        except:
            pass
    return ""

def generate_v4():
    print(f"Reading {input_file}...")
    # Read with appropriate quoting to handle "Name, Year" in references gracefully
    df = pd.read_csv(input_file, quotechar='"', skipinitialspace=True)
    
    headers = df.columns.tolist()
    
    # Identify sample columns range
    non_sample_headers = ['Coluna', 'Referencia', 'DOI', 'Classe química']
    start_sample_idx = 3
    end_sample_idx = len(headers)
    
    for i in range(start_sample_idx, len(headers)):
        if headers[i].strip() in non_sample_headers:
            end_sample_idx = i
            break
    
    sample_cols = headers[start_sample_idx:end_sample_idx]
    print(f"Sample columns: {len(sample_cols)}")
    
    # Identify metadata columns
    col_ref = next((h for h in headers if 'referencia' in h.lower()), None)
    col_doi = next((h for h in headers if 'doi' in h.lower()), None)
    col_class = next((h for h in headers if 'classe' in h.lower()), None)
    col_ir_lit = headers[2]
    col_compound = headers[0]
    col_ir_exp = headers[1]
    
    processed_rows = []
    
    for idx, row in df.iterrows():
        # Compound
        compound = str(row[col_compound]).strip() if pd.notna(row[col_compound]) else ""
        if compound.lower() == 'nan': compound = ""
        
        # Metadata
        chem_class = str(row[col_class]).strip() if col_class and pd.notna(row[col_class]) else ""
        if chem_class.lower() == 'nan': chem_class = ""
        
        ir_lit = clean_simple_number(row[col_ir_lit])
        
        # New: IR Experimental
        # Use simple number cleaning as it's usually a single value
        ir_exp = clean_simple_number(row[col_ir_exp])
        
        # Reference - Clean extra spaces, handle NaN
        ref = str(row[col_ref]).strip() if col_ref and pd.notna(row[col_ref]) else ""
        if ref.lower() == 'nan': ref = ""
        # Ensure we don't end up with internal newlines breaking CSV
        ref = ref.replace('\n', ' ').replace('\r', '') 

        doi = str(row[col_doi]).strip() if col_doi and pd.notna(row[col_doi]) else ""
        if doi.lower() == 'nan': doi = ""
        
        default_ir = row[col_ir_exp]
        
        # Build Found In
        found_parts = []
        for sample in sample_cols:
            raw = row[sample]
            val = clean_value(raw, default_ir)
            if val:
                if val == "Present":
                    found_parts.append(f"{sample}")
                else:
                    found_parts.append(f"{sample} ({val})")
        
        found_str = " | ".join(found_parts)
        
        # ALWAYS append the row, even if found_parts is empty
        processed_rows.append({
            'Compound': compound,
            'Class': chem_class,
            'IR Experimental': ir_exp,
            'IR Literature': ir_lit,
            'Found In': found_str,
            'Reference': ref,
            'DOI': doi
        })
            
    df_out = pd.DataFrame(processed_rows)
    
    output_path = os.path.join(output_dir, 'prototype_3_v4_final.csv')
    
    # Save with semicolon separator and quoting non-numeric
    # QUOTE_ALL or QUOTE_NONNUMERIC ensures Reference fields with commas/semicolons are safe
    df_out.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    generate_v4()
