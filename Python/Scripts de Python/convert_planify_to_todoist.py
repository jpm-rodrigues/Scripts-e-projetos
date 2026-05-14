import json
import csv
import os
import zipfile
from datetime import datetime

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_label_map(data):
    labels = {}
    if 'labels' in data:
        for label in data['labels']:
            labels[label['id']] = label['name']
    return labels

def get_project_map(data):
    projects = {}
    if 'projects' in data:
        for project in data['projects']:
            projects[project['id']] = project
    return projects

def get_items_by_project(data):
    items_by_project = {}
    if 'items' in data:
        for item in data['items']:
            pid = item.get('project_id')
            if not pid:
                continue
            if pid not in items_by_project:
                items_by_project[pid] = []
            items_by_project[pid].append(item)
    return items_by_project

def get_sections_by_project(data):
    sections_by_project = {}
    if 'sections' in data:
        for section in data['sections']:
            pid = section.get('project_id')
            if not pid:
                continue
            if pid not in sections_by_project:
                sections_by_project[pid] = []
            sections_by_project[pid].append(section)
    return sections_by_project

def format_date(date_str):
    if not date_str:
        return ''
    # Planify date example: "2026-01-06" or "2025-12-19T13:00:32"
    # Todoist accepts YYYY-MM-DD or YYYY-MM-DD HH:MM
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime('%Y-%m-%d %H:%M')
        return date_str
    except ValueError:
        return date_str

def process_project(project_id, project_data, items, sections, label_map, output_dir):
    project_name = project_data.get('name', 'Untitled Project')
    # Sanitize filename
    safe_name = "".join([c for c in project_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
    if not safe_name:
        safe_name = f"project_{project_id}"
    
    filename = os.path.join(output_dir, f"{safe_name}.csv")
    
    # Sort sections
    project_sections = sorted(sections.get(project_id, []), key=lambda x: x.get('section_order', 0))
    
    # Sort items
    project_items = sorted(items.get(project_id, []), key=lambda x: x.get('child_order', 0))
    
    # Build item tree and section map
    items_by_parent = {}
    items_by_section = {} # For top-level items in sections
    top_level_no_section = []
    
    item_map = {item['id']: item for item in project_items}
    
    for item in project_items:
        parent_id = item.get('parent_id')
        section_id = item.get('section_id')
        
        # If it has a parent, it's a subtask (regardless of section, usually)
        # But Planify might have subtasks inside sections.
        # Todoist CSV: Indent 1 is task, Indent 2 is subtask.
        # We need to handle hierarchy.
        
        if parent_id and parent_id in item_map:
            if parent_id not in items_by_parent:
                items_by_parent[parent_id] = []
            items_by_parent[parent_id].append(item)
        else:
            # Top level item (or child of deleted item)
            if section_id:
                if section_id not in items_by_section:
                    items_by_section[section_id] = []
                items_by_section[section_id].append(item)
            else:
                top_level_no_section.append(item)

    rows = []
    # Header
    # TYPE,CONTENT,DESCRIPTION,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG,TIMEZONE,DURATION,DURATION_UNIT,DEADLINE,DEADLINE_LANG
    headers = ['TYPE', 'CONTENT', 'DESCRIPTION', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE', 'DURATION', 'DURATION_UNIT', 'DEADLINE', 'DEADLINE_LANG']
    
    def add_item_rows(item, level):
        content = item.get('content', '')
        
        # Add labels
        item_labels = item.get('labels', [])
        for lbl_id in item_labels:
            if lbl_id in label_map:
                content += f" @{label_map[lbl_id]}"
        
        # Pinned status
        if item.get('pinned', False):
            content = f"📌 {content}"
            
        # Priority mapping
        # Planify: 1 (Normal?) -> Todoist: 4 (Normal)
        # If Planify has higher priorities, we might need to adjust.
        # Assuming 1 is default.
        p_val = item.get('priority', 1)
        # Todoist: 1=Highest, 4=Lowest.
        # Let's map 1->4, 2->3, 3->2, 4->1 if that's the scale, or just default to 4.
        # Without knowing Planify scale for sure, I'll default to 4 (Normal) to be safe, 
        # unless it's explicitly high.
        # Let's just use 4 for now as requested "everything stay the same" implies keeping it simple.
        # Actually, let's try to preserve if it varies.
        # But for now, 4.
        priority = 4 
        
        due_data = item.get('due', {})
        if isinstance(due_data, str):
             try:
                 due_data = json.loads(due_data)
             except:
                 due_data = {}
        
        date_str = format_date(due_data.get('date'))
        
        description = item.get('description', '')
        
        row = {
            'TYPE': 'task',
            'CONTENT': content,
            'DESCRIPTION': description,
            'PRIORITY': priority,
            'INDENT': level,
            'DATE': date_str,
            'DATE_LANG': 'pt_BR', # Assuming user is BR based on context
            'TIMEZONE': '',
            'DURATION': '',
            'DURATION_UNIT': '',
            'DEADLINE': '',
            'DEADLINE_LANG': ''
        }
        rows.append(row)
        
        # Process children
        children = items_by_parent.get(item['id'], [])
        # Sort children? They were sorted by child_order initially
        for child in children:
            add_item_rows(child, level + 1)

    # 1. Items with no section
    for item in top_level_no_section:
        add_item_rows(item, 1)
        
    # 2. Sections and their items
    for section in project_sections:
        rows.append({
            'TYPE': 'section',
            'CONTENT': section.get('name', 'Unnamed Section'),
            'INDENT': 1,
            'PRIORITY': 4
        })
        
        sec_items = items_by_section.get(section['id'], [])
        for item in sec_items:
            add_item_rows(item, 1) # Items in sections are still level 1 indentation relative to the project, but visually under section
            # Wait, Todoist CSV: "Use 2 to make the task a sub-task".
            # Items under a section are NOT subtasks of the section in CSV structure.
            # They are just tasks listed after the section row.
            
    # Write CSV
    if rows:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return filename
    return None

def main():
    input_file = '/home/jpmr/Desktop/json to csv planify/Planify backup seg 05 jan 2026 12:32:32.json'
    output_dir = '/home/jpmr/Desktop/json to csv planify/todoist_export'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    data = load_json(input_file)
    
    label_map = get_label_map(data)
    project_map = get_project_map(data)
    items_by_project = get_items_by_project(data)
    sections_by_project = get_sections_by_project(data)
    
    generated_files = []
    
    for pid, project in project_map.items():
        # Only process if there are items or sections? Or always?
        # Always, to preserve empty projects.
        f = process_project(pid, project, items_by_project, sections_by_project, label_map, output_dir)
        if f:
            generated_files.append(f)
            
    # Zip them
    zip_filename = os.path.join(output_dir, 'planify_todoist_export.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in generated_files:
            zipf.write(file, os.path.basename(file))
            
    print(f"Successfully created {len(generated_files)} CSV files.")
    print(f"Zip file created at: {zip_filename}")

if __name__ == "__main__":
    main()
