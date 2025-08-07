#!/usr/bin/env python
"""
Simple Documentation Generator for Parameters and Variables

Creates one page per directory, showing:
- Direct parameters/variables in that directory
- Links to subdirectories
"""

import os
import yaml
import ast
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import defaultdict


class SimpleDocGenerator:
    def __init__(self):
        self.param_dir = Path("policyengine_us/parameters")
        self.var_dir = Path("policyengine_us/variables")
        self.param_output_dir = Path("docs/policy/parameters")
        self.var_output_dir = Path("docs/variables")

    def generate_all(self):
        """Generate documentation for both parameters and variables."""
        print("Generating parameter documentation...")
        self._generate_parameter_docs()
        
        print("Generating variable documentation...")
        self._generate_variable_docs()
        
        print("Documentation generation complete!")

    def _generate_parameter_docs(self):
        """Generate parameter documentation."""
        # Clear and recreate output directory
        if self.param_output_dir.exists():
            shutil.rmtree(self.param_output_dir)
        self.param_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all directories
        self._process_param_directory(self.param_dir, self.param_output_dir, [])

    def _process_param_directory(self, source_dir: Path, output_dir: Path, path_parts: List[str]):
        """Process a parameter directory recursively."""
        # Get contents
        subdirs = []
        param_files = []
        
        for item in sorted(source_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                subdirs.append(item)
            elif item.suffix == '.yaml':
                param_files.append(item)
        
        # Only create documentation if there's content
        if subdirs or param_files:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate index.md for this directory
            self._generate_param_index(output_dir, path_parts, param_files, subdirs)
            
            # Process subdirectories
            for subdir in subdirs:
                new_path_parts = path_parts + [subdir.name]
                self._process_param_directory(
                    subdir, 
                    output_dir / subdir.name,
                    new_path_parts
                )

    def _generate_param_index(self, output_dir: Path, path_parts: List[str], 
                             param_files: List[Path], subdirs: List[Path]):
        """Generate index.md for a parameter directory."""
        lines = []
        
        # Title
        if not path_parts:
            title = "PolicyEngine US Parameters"
        else:
            title = " › ".join(p.upper() for p in path_parts) + " Parameters"
        
        lines.extend([f"# {title}", ""])
        
        # Count total parameters (including subdirectories)
        total_params = len(param_files)
        for subdir in subdirs:
            total_params += self._count_params_recursive(subdir)
        
        if total_params > 0:
            lines.extend([f"This section contains {total_params} parameters.", ""])
        
        # Subdirectories
        if subdirs:
            lines.extend(["## Categories", ""])
            for subdir in subdirs:
                subdir_count = self._count_params_recursive(subdir)
                if subdir_count > 0:
                    lines.append(f"- [{subdir.name.upper()}]({subdir.name}/index.md) ({subdir_count} parameters)")
            lines.append("")
        
        # Direct parameters
        if param_files:
            lines.extend(["## Parameters", ""])
            
            for param_file in param_files:
                param_info = self._load_parameter(param_file)
                if param_info:
                    lines.extend(self._format_parameter(param_file.stem, param_info))
                    lines.append("")
        
        # Write file
        output_file = output_dir / "index.md"
        with open(output_file, "w") as f:
            f.write("\n".join(lines))

    def _count_params_recursive(self, directory: Path) -> int:
        """Count all parameters in a directory recursively."""
        count = 0
        for item in directory.rglob("*.yaml"):
            if not any(skip in str(item) for skip in ['__pycache__', '.git', 'test']):
                count += 1
        return count

    def _load_parameter(self, param_file: Path) -> Dict:
        """Load a parameter from a YAML file."""
        try:
            with open(param_file, "r") as f:
                content = f.read()
                content = content.replace("0000-01-01", "1900-01-01")
                return yaml.safe_load(content)
        except Exception as e:
            print(f"Warning: Error loading {param_file}: {e}")
            return None

    def _format_parameter(self, name: str, data: Dict) -> List[str]:
        """Format a parameter for documentation."""
        lines = []
        
        # Name
        lines.append(f"### `{name}`")
        
        # Label
        if isinstance(data, dict) and "metadata" in data and "label" in data["metadata"]:
            lines.append(f"*{data['metadata']['label']}*")
        
        lines.append("")
        
        # Description
        if isinstance(data, dict) and "description" in data:
            lines.extend([data["description"], ""])
        
        # Key metadata
        if isinstance(data, dict) and "metadata" in data:
            meta = data["metadata"]
            meta_parts = []
            
            if "type" in meta:
                meta_parts.append(f"Type: {meta['type']}")
            if "unit" in meta:
                meta_parts.append(f"Unit: {meta['unit']}")
            if "period" in meta:
                meta_parts.append(f"Period: {meta['period']}")
                
            if meta_parts:
                lines.append("**" + " | ".join(meta_parts) + "**")
                lines.append("")
        
        # Current value
        if isinstance(data, dict) and "values" in data:
            values = data["values"]
            if isinstance(values, dict) and values:
                latest_date = max(values.keys())
                latest_value = values[latest_date]
                lines.append(f"Current value ({latest_date}): **{self._format_value(latest_value)}**")
                lines.append("")
        
        return lines

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, bool):
            return str(value)
        elif isinstance(value, (int, float)):
            if abs(value) >= 1000:
                return f"${value:,.0f}"
            else:
                return f"{value:,.4g}".rstrip("0").rstrip(".")
        elif isinstance(value, list):
            return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return "{complex}"
        return str(value)

    def _generate_variable_docs(self):
        """Generate variable documentation."""
        # Clear and recreate output directory
        if self.var_output_dir.exists():
            shutil.rmtree(self.var_output_dir)
        self.var_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all directories
        self._process_var_directory(self.var_dir, self.var_output_dir, [])

    def _process_var_directory(self, source_dir: Path, output_dir: Path, path_parts: List[str]):
        """Process a variable directory recursively."""
        # Get contents
        subdirs = []
        var_files = []
        
        for item in sorted(source_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                subdirs.append(item)
            elif item.suffix == '.py' and item.name != '__init__.py':
                var_files.append(item)
        
        # Only create documentation if there's content
        if subdirs or var_files:
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate index.md for this directory
            self._generate_var_index(output_dir, path_parts, var_files, subdirs)
            
            # Process subdirectories
            for subdir in subdirs:
                new_path_parts = path_parts + [subdir.name]
                self._process_var_directory(
                    subdir, 
                    output_dir / subdir.name,
                    new_path_parts
                )

    def _generate_var_index(self, output_dir: Path, path_parts: List[str], 
                           var_files: List[Path], subdirs: List[Path]):
        """Generate index.md for a variable directory."""
        lines = []
        
        # Title
        if not path_parts:
            title = "PolicyEngine US Variables"
        else:
            title = " › ".join(p.replace('_', ' ').title() for p in path_parts) + " Variables"
        
        lines.extend([f"# {title}", ""])
        
        # Count total variables (including subdirectories)
        total_vars = 0
        for var_file in var_files:
            if self._is_variable_file(var_file):
                total_vars += 1
        
        for subdir in subdirs:
            total_vars += self._count_vars_recursive(subdir)
        
        if total_vars > 0:
            lines.extend([f"This section contains {total_vars} variables.", ""])
        
        # Subdirectories
        if subdirs:
            lines.extend(["## Categories", ""])
            for subdir in subdirs:
                subdir_count = self._count_vars_recursive(subdir)
                if subdir_count > 0:
                    subdir_title = subdir.name.replace('_', ' ').title()
                    lines.append(f"- [{subdir_title}]({subdir.name}/index.md) ({subdir_count} variables)")
            lines.append("")
        
        # Direct variables
        valid_var_files = [f for f in var_files if self._is_variable_file(f)]
        if valid_var_files:
            lines.extend(["## Variables", ""])
            
            for var_file in valid_var_files:
                var_info = self._extract_variable_info(var_file)
                if var_info:
                    lines.extend(self._format_variable(var_info))
                    lines.append("")
        
        # Write file
        output_file = output_dir / "index.md"
        with open(output_file, "w") as f:
            f.write("\n".join(lines))

    def _count_vars_recursive(self, directory: Path) -> int:
        """Count all variables in a directory recursively."""
        count = 0
        for item in directory.rglob("*.py"):
            if item.name != '__init__.py' and 'test' not in item.name:
                if self._is_variable_file(item):
                    count += 1
        return count

    def _is_variable_file(self, py_file: Path) -> bool:
        """Check if a Python file contains a Variable class."""
        try:
            with open(py_file, "r") as f:
                content = f.read()
            return "class " in content and "Variable" in content
        except:
            return False

    def _extract_variable_info(self, py_file: Path) -> Dict[str, Any]:
        """Extract variable information from a Python file."""
        try:
            with open(py_file, "r") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)
            
            # Find Variable class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Variable":
                            return self._extract_class_info(node, content, py_file)
            
            return None
        except Exception as e:
            print(f"Warning: Error processing {py_file}: {e}")
            return None

    def _extract_class_info(self, class_node: ast.ClassDef, content: str, py_file: Path) -> Dict[str, Any]:
        """Extract information from a Variable class."""
        info = {
            "name": py_file.stem,
            "attributes": {},
            "has_formula": False
        }

        # Extract attributes
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        try:
                            attr_value = ast.literal_eval(node.value)
                            info["attributes"][attr_name] = attr_value
                        except:
                            info["attributes"][attr_name] = None

            # Check for formula
            elif isinstance(node, ast.FunctionDef) and node.name == "formula":
                info["has_formula"] = True

        return info

    def _format_variable(self, var_info: Dict) -> List[str]:
        """Format a variable for documentation."""
        lines = []
        attrs = var_info.get("attributes", {})
        
        # Name
        lines.append(f"### `{var_info['name']}`")
        
        # Label
        if "label" in attrs:
            lines.append(f"*{attrs['label']}*")
        
        lines.append("")
        
        # Key metadata
        meta_parts = []
        
        if "value_type" in attrs:
            meta_parts.append(f"Type: `{attrs['value_type']}`")
        if "entity" in attrs:
            meta_parts.append("Entity: " + str(attrs["entity"]).split('.')[-1])
        if "definition_period" in attrs:
            meta_parts.append(f"Period: {attrs['definition_period']}")
        
        if meta_parts:
            lines.append("**" + " | ".join(meta_parts) + "**")
        
        # Formula indicator
        if var_info.get("has_formula"):
            lines.append("*Calculated variable*")
        elif "default_value" in attrs:
            lines.append(f"*Default: {attrs['default_value']}*")
        
        return lines


def generate_simple_toc():
    """Generate simplified TOC entries."""
    entries = []
    
    # Parameters
    param_dir = Path("docs/policy/parameters")
    if param_dir.exists():
        entries.append("      - file: policy/parameters/index")
        if any(param_dir.iterdir()):
            entries.append("        sections:")
            for item in sorted(param_dir.iterdir()):
                if item.is_dir():
                    entries.append(f"          - file: policy/parameters/{item.name}/index")
    
    # Variables
    var_dir = Path("docs/variables")
    if var_dir.exists():
        entries.append("      - file: variables/index")
        if any(var_dir.iterdir()):
            entries.append("        sections:")
            for item in sorted(var_dir.iterdir()):
                if item.is_dir():
                    entries.append(f"          - file: variables/{item.name}/index")
    
    return entries


if __name__ == "__main__":
    generator = SimpleDocGenerator()
    generator.generate_all()
    
    print("\nTOC entries:")
    for entry in generate_simple_toc():
        print(entry)