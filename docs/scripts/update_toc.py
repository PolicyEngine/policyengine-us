#!/usr/bin/env python
"""Update TOC with the simple documentation structure."""

from pathlib import Path


def generate_toc_entries(base_dir: Path, base_path: str, indent: str = "      "):
    """Generate TOC entries recursively for a directory."""
    entries = []
    
    # Add index for this directory
    entries.append(f"{indent}- file: {base_path}/index")
    
    # Get subdirectories
    subdirs = sorted([d for d in base_dir.iterdir() if d.is_dir()])
    
    if subdirs:
        entries.append(f"{indent}  sections:")
        for subdir in subdirs:
            sub_entries = generate_toc_entries(
                subdir, 
                f"{base_path}/{subdir.name}", 
                indent + "    "
            )
            entries.extend(sub_entries)
    
    return entries


def update_toc():
    """Update the _toc.yml file."""
    toc_path = Path("docs/_toc.yml")
    
    # Read existing TOC
    with open(toc_path, "r") as f:
        lines = f.readlines()
    
    # Find sections to update
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Parameters Reference section
        if "- caption: Parameters Reference" in line:
            new_lines.append(line)
            i += 1
            # Skip to chapters
            while i < len(lines) and "chapters:" not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            new_lines.append(lines[i])  # chapters line
            i += 1
            
            # Generate parameter entries
            param_dir = Path("docs/policy/parameters")
            if param_dir.exists():
                param_entries = generate_toc_entries(param_dir, "policy/parameters")
                new_lines.extend([entry + "\n" for entry in param_entries])
            
            # Skip old entries
            while i < len(lines) and not lines[i].strip().startswith("- caption:"):
                i += 1
            continue
            
        # Variables Reference section
        elif "- caption: Variables Reference" in line:
            new_lines.append(line)
            i += 1
            # Skip to chapters
            while i < len(lines) and "chapters:" not in lines[i]:
                new_lines.append(lines[i])
                i += 1
            new_lines.append(lines[i])  # chapters line
            i += 1
            
            # Generate variable entries
            var_dir = Path("docs/variables")
            if var_dir.exists():
                var_entries = generate_toc_entries(var_dir, "variables")
                new_lines.extend([entry + "\n" for entry in var_entries])
            
            # Skip old entries
            while i < len(lines) and not lines[i].strip().startswith("- caption:"):
                i += 1
            continue
        
        else:
            new_lines.append(line)
            i += 1
    
    # Write updated TOC
    with open(toc_path, "w") as f:
        f.writelines(new_lines)
    
    print(f"Updated {toc_path}")


if __name__ == "__main__":
    update_toc()