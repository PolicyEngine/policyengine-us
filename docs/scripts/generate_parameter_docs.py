#!/usr/bin/env python
"""
Automated Parameter Documentation Generator

This script generates comprehensive documentation for all parameters
in PolicyEngine US, extracting metadata, legislative references,
and historical values.
"""

import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ParameterDocGenerator:
    def __init__(self, param_dir: str = "policyengine_us/parameters"):
        self.param_dir = Path(param_dir)
        self.output_dir = Path("docs/policy/parameters")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_all_parameters(self):
        """Process all parameter files and generate documentation."""
        parameters_by_category = {}

        # Walk through parameter directory
        for yaml_file in self.param_dir.rglob("*.yaml"):
            if yaml_file.name == "__pycache__":
                continue

            # Load parameter
            with open(yaml_file, "r") as f:
                try:
                    param_data = yaml.safe_load(f)
                except:
                    continue

            # Categorize by path
            category = self._get_category(yaml_file)
            if category not in parameters_by_category:
                parameters_by_category[category] = []

            parameters_by_category[category].append(
                {"path": yaml_file, "data": param_data, "name": yaml_file.stem}
            )

        # Generate documentation for each category
        for category, params in parameters_by_category.items():
            self._generate_category_docs(category, params)

        # Generate master index
        self._generate_index(parameters_by_category)

    def _get_category(self, path: Path) -> str:
        """Extract category from file path."""
        rel_path = path.relative_to(self.param_dir)
        parts = rel_path.parts[:-1]  # Remove filename

        if len(parts) >= 2 and parts[0] == "gov":
            return parts[1]  # IRS, SSA, USDA, etc.
        return "other"

    def _generate_category_docs(self, category: str, params: List[Dict]):
        """Generate documentation for a parameter category."""
        output_file = self.output_dir / f"{category}.md"

        content = [
            f"# {category.upper()} Parameters",
            "",
            f"This section documents all {category.upper()} parameters in PolicyEngine US.",
            "",
            "## Parameter List",
            "",
        ]

        # Sort parameters by name
        params.sort(key=lambda x: x["name"])

        for param in params:
            param_doc = self._format_parameter(param)
            content.extend(param_doc)
            content.append("")

        # Write file
        with open(output_file, "w") as f:
            f.write("\n".join(content))

    def _format_parameter(self, param: Dict) -> List[str]:
        """Format a single parameter's documentation."""
        data = param["data"]
        if not isinstance(data, dict):
            return []

        lines = [f"### {param['name']}", ""]

        # Description
        if "description" in data:
            lines.extend(["**Description**: " + data["description"], ""])

        # Metadata
        if "metadata" in data:
            meta = data["metadata"]

            if "unit" in meta:
                lines.append(f"**Unit**: {meta['unit']}")

            if "period" in meta:
                lines.append(f"**Period**: {meta['period']}")

            if "reference" in meta:
                lines.extend(["", "**References**:"])
                for ref in meta["reference"]:
                    if isinstance(ref, dict):
                        title = ref.get("title", "Unknown")
                        href = ref.get("href", "")
                        lines.append(f"- [{title}]({href})")
                    else:
                        lines.append(f"- {ref}")

            if "uprating" in meta:
                lines.append(f"**Inflation Adjustment**: {meta['uprating']}")

            lines.append("")

        # Values over time
        if "values" in data:
            lines.extend(["**Historical Values**:", ""])
            lines.append("| Date | Value |")
            lines.append("|------|-------|")

            # Handle different value structures
            if isinstance(data["values"], dict):
                for date, value in sorted(data["values"].items()):
                    lines.append(f"| {date} | {self._format_value(value)} |")
            elif isinstance(data["values"], list):
                for item in data["values"]:
                    if "instant" in item:
                        date = item["instant"]
                        value = item.get("value", "N/A")
                        lines.append(
                            f"| {date} | {self._format_value(value)} |"
                        )

            lines.append("")

        # Breakdowns
        if "brackets" in data:
            lines.extend(["**Brackets**:", ""])
            for bracket in data["brackets"]:
                if isinstance(bracket, dict):
                    lines.append(self._format_bracket(bracket))
            lines.append("")

        # Policy notes
        if "policy_notes" in data:
            lines.extend(["**Policy Notes**:", data["policy_notes"], ""])

        # Variable path
        rel_path = param["path"].relative_to(self.param_dir)
        lines.extend([f"**Parameter Path**: `{rel_path}`", ""])

        return lines

    def _format_value(self, value: Any) -> str:
        """Format parameter value for display."""
        if isinstance(value, (int, float)):
            if value > 1000:
                return f"${value:,.0f}"
            else:
                return f"{value:,.4g}".rstrip("0").rstrip(".")
        return str(value)

    def _format_bracket(self, bracket: Dict) -> str:
        """Format tax bracket information."""
        parts = []
        if "threshold" in bracket:
            parts.append(f"Above ${bracket['threshold']:,.0f}")
        if "rate" in bracket:
            parts.append(f"{bracket['rate']*100:.1f}%")
        if "amount" in bracket:
            parts.append(f"${bracket['amount']:,.0f}")
        return " - " + ", ".join(parts)

    def _generate_index(self, parameters_by_category: Dict):
        """Generate master parameter index."""
        index_file = self.output_dir / "index.md"

        content = [
            "# PolicyEngine US Parameter Reference",
            "",
            "This reference documents all parameters used in PolicyEngine US calculations.",
            "",
            "## Categories",
            "",
        ]

        for category in sorted(parameters_by_category.keys()):
            count = len(parameters_by_category[category])
            content.append(
                f"- [{category.upper()}]({category}.md) ({count} parameters)"
            )

        content.extend(
            [
                "",
                "## About Parameters",
                "",
                "Parameters in PolicyEngine US represent legislative values such as:",
                "- Tax rates and brackets",
                "- Benefit amounts and thresholds",
                "- Phase-out ranges and percentages",
                "- Standard deductions and exemptions",
                "",
                "All parameters include:",
                "- **Legislative references**: Links to statutes and regulations",
                "- **Historical values**: Changes over time",
                "- **Metadata**: Units, inflation adjustment methods",
                "- **Policy notes**: Implementation details",
                "",
                "## Automated Generation",
                "",
                "This documentation is automatically generated from the parameter files.",
                f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ]
        )

        with open(index_file, "w") as f:
            f.write("\n".join(content))


def generate_variable_docs():
    """Generate documentation for all variables."""
    from policyengine_us import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()

    output_dir = Path("docs/policy/variables")
    output_dir.mkdir(parents=True, exist_ok=True)

    variables_by_module = {}

    # Group variables by module
    for var_name, var_class in system.variables.items():
        module = var_class.__module__.split(".")[-2]  # Get category
        if module not in variables_by_module:
            variables_by_module[module] = []

        variables_by_module[module].append(
            {
                "name": var_name,
                "class": var_class,
                "label": getattr(var_class, "label", var_name),
                "unit": getattr(var_class, "unit", None),
                "entity": getattr(var_class, "entity", None),
                "definition_period": getattr(
                    var_class, "definition_period", None
                ),
                "documentation": getattr(var_class, "documentation", ""),
                "reference": getattr(var_class, "reference", []),
            }
        )

    # Generate documentation for each module
    for module, variables in variables_by_module.items():
        generate_module_variable_docs(module, variables, output_dir)

    # Generate index
    generate_variable_index(variables_by_module, output_dir)


def generate_module_variable_docs(
    module: str, variables: List[Dict], output_dir: Path
):
    """Generate documentation for variables in a module."""
    output_file = output_dir / f"{module}.md"

    content = [
        f"# {module.title()} Variables",
        "",
        f"This section documents all variables in the {module} module.",
        "",
        "## Variable List",
        "",
    ]

    # Sort by name
    variables.sort(key=lambda x: x["name"])

    for var in variables:
        content.extend(
            [
                f"### {var['name']}",
                "",
                f"**Label**: {var['label']}",
                f"**Entity**: {var['entity'].__name__ if var['entity'] else 'Unknown'}",
                f"**Period**: {var['definition_period']}",
            ]
        )

        if var["unit"]:
            content.append(f"**Unit**: {var['unit']}")

        if var["documentation"]:
            content.extend(["", var["documentation"]])

        if var["reference"]:
            content.extend(["", "**References**:"])
            for ref in var["reference"]:
                content.append(f"- {ref}")

        content.append("")

    with open(output_file, "w") as f:
        f.write("\n".join(content))


def generate_variable_index(variables_by_module: Dict, output_dir: Path):
    """Generate variable index."""
    index_file = output_dir / "index.md"

    content = [
        "# PolicyEngine US Variable Reference",
        "",
        "Complete reference of all variables calculated by PolicyEngine US.",
        "",
        "## Modules",
        "",
    ]

    for module in sorted(variables_by_module.keys()):
        count = len(variables_by_module[module])
        content.append(
            f"- [{module.title()}]({module}.md) ({count} variables)"
        )

    with open(index_file, "w") as f:
        f.write("\n".join(content))


if __name__ == "__main__":
    # Generate parameter documentation
    print("Generating parameter documentation...")
    doc_gen = ParameterDocGenerator()
    doc_gen.process_all_parameters()

    # Generate variable documentation
    print("Generating variable documentation...")
    generate_variable_docs()

    print("Documentation generation complete!")
