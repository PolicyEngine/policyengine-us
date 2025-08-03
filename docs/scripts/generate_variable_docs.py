#!/usr/bin/env python3
"""
Generate comprehensive documentation for all PolicyEngine US variables.

This script extracts metadata from all variables and creates structured
documentation organized by module hierarchy.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any
import importlib.util
import inspect
from collections import defaultdict


class VariableDocGenerator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.variables_dir = repo_root / "policyengine_us" / "variables"
        self.docs_dir = repo_root / "docs" / "variables"
        self.variables_by_module = defaultdict(list)
        
    def extract_variable_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from a variable Python file."""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            module = importlib.util.module_from_spec(spec)
            
            # Import model_api to make Variable available
            import sys
            sys.path.insert(0, str(self.repo_root))
            from policyengine_us.model_api import Variable
            
            # Execute the module
            spec.loader.exec_module(module)
            
            # Find Variable subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Variable) and 
                    obj is not Variable):
                    
                    # Extract metadata
                    metadata = {
                        "name": name,
                        "label": getattr(obj, "label", ""),
                        "unit": getattr(obj, "unit", ""),
                        "entity": getattr(obj, "entity", "").__name__ if hasattr(obj, "entity") else "",
                        "definition_period": getattr(obj, "definition_period", ""),
                        "value_type": getattr(obj, "value_type", "").__name__ if hasattr(obj, "value_type") else "",
                        "reference": getattr(obj, "reference", ""),
                        "documentation": getattr(obj, "documentation", ""),
                        "defined_for": getattr(obj, "defined_for", ""),
                        "file_path": str(file_path.relative_to(self.repo_root)),
                        "module_path": self._get_module_path(file_path),
                    }
                    
                    # Handle references - could be string or list
                    if isinstance(metadata["reference"], list):
                        metadata["references"] = metadata["reference"]
                    elif metadata["reference"]:
                        metadata["references"] = [metadata["reference"]]
                    else:
                        metadata["references"] = []
                    
                    return metadata
                    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
        return None
    
    def _get_module_path(self, file_path: Path) -> str:
        """Get the module path relative to variables directory."""
        rel_path = file_path.relative_to(self.variables_dir)
        return str(rel_path.parent).replace(os.sep, ".")
    
    def collect_all_variables(self):
        """Collect metadata for all variables in the codebase."""
        for py_file in self.variables_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            metadata = self.extract_variable_metadata(py_file)
            if metadata:
                module = metadata["module_path"]
                self.variables_by_module[module].append(metadata)
    
    def generate_module_docs(self, module: str, variables: List[Dict]) -> str:
        """Generate documentation for a module's variables."""
        # Create title from module path
        parts = module.split(".")
        title_parts = []
        
        # Expand common abbreviations
        abbreviations = {
            "gov": "Government",
            "irs": "Internal Revenue Service",
            "ssa": "Social Security Administration",
            "hhs": "Health and Human Services",
            "usda": "Department of Agriculture",
            "hud": "Housing and Urban Development",
            "ed": "Department of Education",
            "snap": "SNAP",
            "tanf": "TANF",
            "ssi": "SSI",
            "ctc": "Child Tax Credit",
            "eitc": "Earned Income Tax Credit",
        }
        
        for part in parts:
            expanded = abbreviations.get(part, part.replace("_", " ").title())
            title_parts.append(expanded)
        
        title = " / ".join(title_parts)
        
        # Start document
        lines = [
            f"# {title}",
            "",
            f"This section contains {len(variables)} variables.",
            "",
        ]
        
        # Add table of contents
        if len(variables) > 5:
            lines.extend([
                "## Table of Contents",
                "",
            ])
            for var in sorted(variables, key=lambda x: x["name"]):
                anchor = var["name"].replace("_", "-")
                lines.append(f"- [{var['name']}](#{anchor})")
            lines.append("")
        
        # Document each variable
        for var in sorted(variables, key=lambda x: x["name"]):
            lines.extend([
                f"## {var['name']}",
                "",
            ])
            
            # Basic metadata table
            lines.extend([
                "| Attribute | Value |",
                "|-----------|-------|",
                f"| Label | {var['label']} |",
                f"| Unit | {var['unit'] or 'N/A'} |",
                f"| Entity | {var['entity']} |",
                f"| Period | {var['definition_period']} |",
                f"| Value Type | {var['value_type']} |",
            ])
            
            if var["defined_for"]:
                lines.append(f"| Defined For | `{var['defined_for']}` |")
                
            lines.append("")
            
            # Documentation
            if var["documentation"]:
                lines.extend([
                    "### Description",
                    "",
                    var["documentation"].strip(),
                    "",
                ])
            
            # References
            if var["references"]:
                lines.extend([
                    "### References",
                    "",
                ])
                for ref in var["references"]:
                    if isinstance(ref, dict) and "title" in ref:
                        lines.append(f"- [{ref['title']}]({ref.get('href', '#')})")
                    else:
                        lines.append(f"- {ref}")
                lines.append("")
            
            # Source code link
            lines.extend([
                "### Implementation",
                "",
                f"- Source: [`{var['file_path']}`](https://github.com/PolicyEngine/policyengine-us/blob/master/{var['file_path']})",
                "",
            ])
        
        return "\n".join(lines)
    
    def generate_index(self) -> str:
        """Generate the main index page for variables documentation."""
        lines = [
            "# PolicyEngine US Variables Reference",
            "",
            "This reference documents all variables computed by PolicyEngine US, organized by government agency and program.",
            "",
            "```{toctree}",
            ":maxdepth: 3",
            "",
        ]
        
        # Organize modules hierarchically
        module_tree = {}
        for module in sorted(self.variables_by_module.keys()):
            parts = module.split(".")
            current = module_tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Generate toctree entries
        def add_entries(tree, prefix=""):
            entries = []
            for key in sorted(tree.keys()):
                if prefix:
                    path = f"{prefix}.{key}"
                else:
                    path = key
                    
                # Check if this module has variables
                if path in self.variables_by_module:
                    entries.append(path.replace(".", "/"))
                    
                # Recurse for submodules
                if tree[key]:
                    entries.extend(add_entries(tree[key], path))
                    
            return entries
        
        entries = add_entries(module_tree)
        lines.extend(entries)
        lines.extend([
            "```",
            "",
            "## Overview",
            "",
            f"PolicyEngine US models {len(self.variables_by_module)} modules containing "
            f"{sum(len(v) for v in self.variables_by_module.values())} variables.",
            "",
            "### Organization",
            "",
            "Variables are organized by:",
            "- **Agency**: The administering government agency (IRS, SSA, USDA, etc.)",
            "- **Program**: The specific program or tax provision",
            "- **Concept**: The type of calculation (eligibility, income, deduction, credit, etc.)",
            "",
            "### Variable Attributes",
            "",
            "Each variable includes:",
            "- **Label**: Human-readable name",
            "- **Unit**: USD for monetary values, otherwise unitless",
            "- **Entity**: Person, TaxUnit, SPMUnit, or Household",
            "- **Period**: YEAR, MONTH, WEEK, or ETERNITY",
            "- **References**: Legislative citations and regulatory sources",
            "",
        ])
        
        return "\n".join(lines)
    
    def write_documentation(self):
        """Write all documentation files."""
        # Create docs directory
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Write index
        index_content = self.generate_index()
        (self.docs_dir / "index.md").write_text(index_content)
        print(f"Generated {self.docs_dir / 'index.md'}")
        
        # Write module documentation
        for module, variables in self.variables_by_module.items():
            # Create directory structure
            module_path = self.docs_dir / module.replace(".", "/")
            module_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate and write content
            content = self.generate_module_docs(module, variables)
            doc_file = module_path.with_suffix(".md")
            doc_file.write_text(content)
            print(f"Generated {doc_file}")
    
    def generate(self):
        """Run the full documentation generation process."""
        print("Collecting variable metadata...")
        self.collect_all_variables()
        
        print(f"Found {sum(len(v) for v in self.variables_by_module.values())} variables in {len(self.variables_by_module)} modules")
        
        print("Writing documentation...")
        self.write_documentation()
        
        print("\nDocumentation generation complete!")


def main():
    """Generate variable documentation."""
    repo_root = Path(__file__).parent.parent.parent
    generator = VariableDocGenerator(repo_root)
    generator.generate()


if __name__ == "__main__":
    main()