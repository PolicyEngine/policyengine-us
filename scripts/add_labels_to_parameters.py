#!/usr/bin/env python3
"""
Script to add human-readable labels to parameters that don't have them.

This script:
1. Walks through all parameter YAML files
2. Identifies parameters without labels
3. Generates labels by humanizing parameter names
4. Adds the labels to the YAML files (preserving formatting)
"""

import re
from pathlib import Path

from ruamel.yaml import YAML


def humanize_name(name) -> str:
    """
    Convert a snake_case or camelCase name to a human-readable label.

    Examples:
        taxable_interest_and_ordinary_dividends -> Taxable interest and ordinary dividends
        net_capital_gain -> Net capital gain
        qbi -> QBI
        eitc -> EITC
        agi -> AGI
    """
    # Convert to string if not already
    name = str(name)

    # Known acronyms that should stay uppercase
    acronyms = {
        'agi', 'qbi', 'eitc', 'ctc', 'cdcc', 'snap', 'tanf', 'ssi', 'ssdi',
        'aca', 'irs', 'cbo', 'hhs', 'usda', 'fpl', 'amt', 'niit', 'salt',
        'oasdi', 'fica', 'magi', 'spm', 'cola', 'ui', 'wic', 'liheap',
        'dc', 'ny', 'ca', 'tx', 'fl', 'il', 'pa', 'oh', 'ga', 'nc', 'mi',
        'nj', 'va', 'wa', 'az', 'ma', 'tn', 'in', 'md', 'mo', 'wi', 'co',
        'mn', 'sc', 'al', 'la', 'ky', 'or', 'ok', 'ct', 'ut', 'ia', 'nv',
        'ar', 'ms', 'ks', 'nm', 'ne', 'id', 'wv', 'hi', 'nh', 'me', 'mt',
        'ri', 'de', 'sd', 'nd', 'ak', 'vt', 'wy', 'pr', 'vi', 'gu', 'as',
        'usa', 'us', 'uk', 'id', 'pr', 'soi', 'cps', 'puf', 'atr', 'pct',
        'max', 'min', 'avg', 'std', 'var', 'cpi', 'gdp', 'gni', 'sai',
        'ptc', 'chip', 'cms', 'awra', 'nyc', 'stc', 'cvrp', 'carb',
        'kccatc', 'calepa',
    }

    # Replace underscores with spaces
    result = name.replace('_', ' ')

    # Split into words
    words = result.split()

    # Process each word
    processed_words = []
    for i, word in enumerate(words):
        word_lower = word.lower()
        if word_lower in acronyms:
            processed_words.append(word.upper())
        elif i == 0:
            # Capitalize first word
            processed_words.append(word.capitalize())
        else:
            processed_words.append(word.lower())

    return ' '.join(processed_words)


def is_parameter_key(key, value) -> bool:
    """
    Determine if a YAML key represents a parameter where we can safely add labels.

    We can only add labels to parameters that already have a 'values' or 'metadata'
    sub-key, because adding metadata to keys that have direct date values would
    break the parameter structure.
    """
    # Skip numeric keys (likely array indices or year-based data)
    if isinstance(key, (int, float)):
        return False

    reserved_keys = {
        'description', 'metadata', 'values', 'brackets', 'reference',
        'threshold', 'rate', 'amount', 'label', 'unit', 'period',
        'uprating', 'propagate_metadata_to_children', 'type',
        'threshold_period', 'threshold_unit', 'rate_unit', 'amount_unit',
    }

    if key in reserved_keys:
        return False

    if not hasattr(value, 'keys'):
        return False

    # Only return True if the value has 'values' or 'metadata' sub-key
    # Do NOT return True for keys with direct date values, as adding metadata
    # to those would break the parameter structure
    for k in value.keys():
        if k in ('values', 'metadata'):
            return True

    return False


def parameter_has_label(param_data) -> bool:
    """Check if a parameter already has a label in its metadata."""
    if not hasattr(param_data, 'get'):
        return False

    metadata = param_data.get('metadata', {})
    if hasattr(metadata, 'get') and metadata.get('label'):
        return True

    return False


def add_label_to_parameter(param_data, label: str):
    """Add a label to a parameter's metadata."""
    if 'metadata' not in param_data:
        param_data['metadata'] = {}

    if not hasattr(param_data['metadata'], '__setitem__'):
        param_data['metadata'] = {}

    param_data['metadata']['label'] = label


def get_file_description(data) -> str | None:
    """Get the description from a YAML file."""
    if hasattr(data, 'get'):
        return data.get('description')
    return None


def file_has_top_level_label(data) -> bool:
    """Check if the file has a top-level label (in metadata)."""
    if not hasattr(data, 'get'):
        return False
    metadata = data.get('metadata', {})
    return hasattr(metadata, 'get') and metadata.get('label')


def add_top_level_label(data, label: str):
    """Add a label to the file's top-level metadata."""
    if 'metadata' not in data:
        data['metadata'] = {}

    if not hasattr(data['metadata'], '__setitem__'):
        data['metadata'] = {}

    data['metadata']['label'] = label


def process_yaml_file(filepath: Path, yaml: YAML) -> tuple[bool, int]:
    """
    Process a YAML file to add labels to parameters without them.

    Returns:
        Tuple of (was_modified, num_labels_added)
    """
    try:
        with open(filepath, 'r') as f:
            data = yaml.load(f)
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return False, 0

    if data is None:
        return False, 0

    modified = False
    labels_added = 0

    # Get the filename without extension for generating labels
    filename = filepath.stem

    # Check if this is a single-parameter file (has 'values' or 'brackets' at top level)
    is_single_param_file = 'values' in data or 'brackets' in data

    if is_single_param_file:
        # This file represents a single parameter
        if not file_has_top_level_label(data):
            # Generate label from filename or description
            description = get_file_description(data)
            if description:
                # Use first sentence of description as label
                label = description.split('.')[0].strip()
                # Limit length
                if len(label) > 80:
                    label = humanize_name(filename)
            else:
                label = humanize_name(filename)

            add_top_level_label(data, label)
            modified = True
            labels_added += 1
    else:
        # This file may contain multiple parameters as keys
        for key in list(data.keys()):
            value = data[key]
            if is_parameter_key(key, value):
                if not parameter_has_label(value):
                    label = humanize_name(key)
                    add_label_to_parameter(value, label)
                    modified = True
                    labels_added += 1

    if modified:
        with open(filepath, 'w') as f:
            yaml.dump(data, f)

    return modified, labels_added


def main():
    """Main function to process all parameter YAML files."""
    parameters_dir = Path(__file__).parent.parent / 'policyengine_us' / 'parameters'

    if not parameters_dir.exists():
        print(f"Parameters directory not found: {parameters_dir}")
        return

    # Create YAML instance with round-trip mode (preserves formatting)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096  # Avoid line wrapping

    # Override the timestamp constructor to handle year 0 dates
    from ruamel.yaml.scalarstring import PlainScalarString
    from datetime import date

    original_constructor = yaml.Constructor.yaml_constructors.get(
        'tag:yaml.org,2002:timestamp'
    )

    def timestamp_constructor(loader, node):
        value = node.value
        # Try to parse as date first
        try:
            if original_constructor:
                return original_constructor(loader, node)
        except (ValueError, TypeError):
            # If parsing fails (e.g., year 0), return as plain string
            return PlainScalarString(value)
        return PlainScalarString(value)

    yaml.Constructor.add_constructor(
        'tag:yaml.org,2002:timestamp', timestamp_constructor
    )

    total_files = 0
    modified_files = 0
    total_labels_added = 0

    for yaml_file in parameters_dir.rglob('*.yaml'):
        total_files += 1
        was_modified, labels_added = process_yaml_file(yaml_file, yaml)
        if was_modified:
            modified_files += 1
            total_labels_added += labels_added
            print(f"Modified: {yaml_file.relative_to(parameters_dir)} (+{labels_added} labels)")

    print(f"\nSummary:")
    print(f"  Total files processed: {total_files}")
    print(f"  Files modified: {modified_files}")
    print(f"  Labels added: {total_labels_added}")


if __name__ == '__main__':
    main()
