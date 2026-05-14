import pandas as pd
import re
import os
import sys

# Paths
original_file = '/home/jpmr/Desktop/AI test/Coisa naj/JP_tabela geral_CGEM_copia.csv'
final_file = '/home/jpmr/Desktop/AI test/Coisa naj/prototype_3_v4_final.csv'

# --- Reuse Parsing Logic to determine expected values ---
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

def clean_value(cell, default_ir):
    """Same logic as v4 script to determine what SHOULD be there."""
    if pd.isna(cell) or str(cell).strip() == '':
        return None
    
    s = str(cell).strip()
    
    is_present_marker = False
    if s.lower() == 'x' or s.lower() == 'xx':
        is_present_marker = True
    elif 'x' in s.lower(): 
        is_present_marker = True
        
    found_numbers = re.findall(r'\d+(?:\.\d+)?', s)
    
    cleaned_list = []
    for num_str in found_numbers:
        try:
            val = float(num_str)
            cleaned_list.append(val)
        except:
            continue
            
    if cleaned_list:
        unique_vals = sorted(list(set(cleaned_list)))
        str_vals = []
        for v in unique_vals:
            if v.is_integer():
                str_vals.append(str(int(v)))
            else:
                str_vals.append(str(v))
        return ", ".join(str_vals)
    
    elif is_present_marker:
        clean_default = clean_simple_number(default_ir)
        if clean_default:
            return clean_default
        else:
            return "Present"
            
    return None

def verify():
    print("Loading files...")
    df_orig = pd.read_csv(original_file, quotechar='"', skipinitialspace=True)
    
    # Read final with semicolon
    df_final = pd.read_csv(final_file, sep=';', quotechar='"')
    
    # --- Identify Columns in Original ---
    headers = df_orig.columns.tolist()
    non_sample_headers = ['Coluna', 'Referencia', 'DOI', 'Classe química']
    start_sample_idx = 3
    end_sample_idx = len(headers)
    for i in range(start_sample_idx, len(headers)):
        if headers[i].strip() in non_sample_headers:
            end_sample_idx = i
            break
    sample_cols = headers[start_sample_idx:end_sample_idx]
    col_ir_exp = headers[1] # IR experimental
    
    print(f"Verifying {len(df_orig)} rows across {len(sample_cols)} sample columns...")
    
    errors = []
    total_checks = 0
    passed_checks = 0
    
    # Ideally iterate by index assuming 1:1 mapping (which our script maintained)
    if len(df_orig) != len(df_final):
        print(f"CRITICAL WARNING: Row count mismatch! Original: {len(df_orig)}, Final: {len(df_final)}")
        # We try to match by Compound name
        # Build dict of final rows
        final_map = {}
        for idx, row in df_final.iterrows():
            c = str(row['Compound']).strip()
            final_map[c] = row['Found In']
    else:
        final_map = None # Use index matching
        
    for idx, row_orig in df_orig.iterrows():
        # Get corresponding final row
        if final_map:
            comp_name = str(row_orig[headers[0]]).strip()
            if comp_name not in final_map:
                errors.append(f"Row {idx+2}: Compound '{comp_name}' missing in final file.")
                continue
            found_in_str = str(final_map[comp_name])
        else:
            found_in_str = str(df_final.iloc[idx]['Found In'])
            
        # Parse Found In string into a set of tokens for faster lookup
        # Format: "Sample (Value) | Sample2 (Value2)"
        # We just checking if expected substring exists is usually enough and robust
        
        default_ir = row_orig[col_ir_exp]
        
        for sample in sample_cols:
            raw_val = row_orig[sample]
            expected_val = clean_value(raw_val, default_ir)
            
            if expected_val:
                total_checks += 1
                
                # Construct exact expected string
                if expected_val == "Present":
                    # Check for "SampleName" but ensure it's not "SampleNameX"
                    # However, splitted by pipe " | " makes it discrete tokens.
                    pass
                else:
                    pass
                    
                # Robust check: Split the found_in_str by ' | '
                found_tokens = [t.strip() for t in found_in_str.split('|')]
                
                expected_token = ""
                if expected_val == "Present":
                    expected_token = f"{sample}"
                else:
                    expected_token = f"{sample} ({expected_val})"
                
                # Check if exact token exists
                if expected_token not in found_tokens:
                    # Try partial match? Maybe whitespace diff?
                    # Be lenient with spacing
                    found_clean = [t.replace(" ", "") for t in found_tokens]
                    expected_clean = expected_token.replace(" ", "")
                    
                    if expected_clean not in found_clean:
                        errors.append(f"Row {idx+2} ({row_orig[headers[0]]}): Missing '{expected_token}'. Raw: '{raw_val}'")
                    else:
                        passed_checks += 1
                else:
                    passed_checks += 1

    print("-" * 30)
    print(f"Verification Complete.")
    print(f"Total Non-Empty Cells Checked: {total_checks}")
    print(f"Passed: {passed_checks}")
    if errors:
        print(f"FAILED: {len(errors)} mismatches found.")
        print("Example Errors:")
        for e in errors[:10]:
            print(" - " + e)
    else:
        print("SUCCESS: All data verified perfectly.")

if __name__ == "__main__":
    verify()
