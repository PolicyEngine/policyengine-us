import pandas as pd
import yaml
import os

def create_age_curve_yamls():
    # Define the states (excluding New Jersey)
    states = ['Default', 'Alabama', 'District of Columbia', 'Massachusetts', 
              'Minnesota', 'Mississippi', 'Oregon', 'Utah']
    
    # Create data structure for each state
    for state in states:
        # Create the base YAML structure
        yaml_data = {
            "description": f"Age curve factors for ACA premium pricing in {state}, normalized to age 0.",
            "metadata": {
                "type": "age_rate",
                "period": "year",
                "rate_unit": "/1",
                "label": f"ACA premium age curve factors - {state}",
                "reference": [{
                    "title": "CMS Market Rating Reforms State Specific Age Curve Variations",
                    "href": "https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/downloads/statespecagecrv053117.pdf"
                }]
            },
            "brackets": []
        }
        
        # Get normalization factor (value for age 0-14)
        if state == 'Default':
            norm_factor = 0.765
        elif state in ['Alabama', 'Mississippi', 'Oregon']:
            norm_factor = 0.635
        elif state == 'District of Columbia':
            norm_factor = 0.654
        elif state == 'Massachusetts':
            norm_factor = 0.751
        elif state == 'Minnesota':
            norm_factor = 0.890
        elif state == 'Utah':
            norm_factor = 0.793
        
        # Add age brackets
        # First the 0-14 bracket
        yaml_data["brackets"].append({
            "age": {"0000-01-01": "0-14"},
            "rate": {"0000-01-01": "1.0000"}
        })
        
        # Ages 15-20
        age_15_20_values = {
            'Default': [0.833, 0.859, 0.885, 0.913, 0.941, 0.970],
            'Alabama': [0.635, 0.635, 0.635, 0.635, 0.635, 0.635],
            'District of Columbia': [0.654, 0.654, 0.654, 0.654, 0.654, 0.654],
            'Massachusetts': [0.751, 0.751, 0.751, 0.751, 0.751, 0.751],
            'Minnesota': [0.890, 0.890, 0.890, 0.890, 0.890, 0.890],
            'Mississippi': [0.635, 0.635, 0.635, 0.635, 0.635, 0.635],
            'Oregon': [0.635, 0.635, 0.635, 0.635, 0.635, 0.635],
            'Utah': [0.793, 0.793, 0.793, 0.793, 0.793, 0.793]
        }
        
        for age, value in zip(range(15, 21), age_15_20_values[state]):
            yaml_data["brackets"].append({
                "age": {"0000-01-01": str(age)},
                "rate": {"0000-01-01": f"{value/norm_factor:.4f}"}
            })
        
        # Ages 21+
        age_values = {
            'Default': {21: 1.000, 25: 1.004, 30: 1.135, 35: 1.222, 40: 1.278, 45: 1.444,
                       50: 1.786, 55: 2.230, 60: 2.714, 64: 3.000},
            'Alabama': {21: 1.000, 25: 1.004, 30: 1.135, 35: 1.222, 40: 1.278, 45: 1.444,
                       50: 1.786, 55: 2.230, 60: 2.714, 64: 3.000},
            'District of Columbia': {21: 0.727, 25: 0.727, 30: 0.779, 35: 0.876, 40: 0.975,
                                   45: 1.181, 50: 1.431, 55: 1.733, 60: 2.099, 64: 2.181},
            'Massachusetts': {21: 1.183, 25: 1.183, 30: 1.287, 35: 1.352, 40: 1.393,
                            45: 1.511, 50: 1.741, 55: 2.019, 60: 2.365, 64: 2.365},
            'Minnesota': {21: 1.000, 25: 1.004, 30: 1.135, 35: 1.222, 40: 1.278,
                         45: 1.444, 50: 1.786, 55: 2.230, 60: 2.714, 64: 3.000},
            'Mississippi': {21: 1.000, 25: 1.004, 30: 1.135, 35: 1.222, 40: 1.278,
                          45: 1.444, 50: 1.786, 55: 2.230, 60: 2.714, 64: 3.000},
            'Oregon': {21: 1.000, 25: 1.004, 30: 1.135, 35: 1.222, 40: 1.278,
                      45: 1.444, 50: 1.786, 55: 2.230, 60: 2.714, 64: 3.000},
            'Utah': {21: 1.000, 25: 1.298, 30: 1.390, 35: 1.390, 40: 1.479,
                    45: 1.748, 50: 2.127, 55: 2.588, 60: 3.000, 64: 3.000}
        }
        
        for age in range(21, 65):
            # Find the closest age in our age_values dictionary
            closest_age = min([k for k in age_values[state].keys() if k <= age], 
                            key=lambda x: abs(x - age))
            rate = age_values[state][closest_age]
            
            yaml_data["brackets"].append({
                "age": {"0000-01-01": str(age)},
                "rate": {"0000-01-01": f"{rate/norm_factor:.4f}"}
            })
        
        # Create directory if it doesn't exist
        os.makedirs('age_curves', exist_ok=True)
        
        # Save to YAML file
        filename = f'age_curves/age_curve_{state.lower().replace(" ", "_")}.yaml'
        with open(filename, 'w') as f:
            yaml.dump(yaml_data, f, sort_keys=False, allow_unicode=True)
        
        print(f"Created YAML file for {state}")

if __name__ == "__main__":
    create_age_curve_yamls()
    print("\nAll YAML files have been created successfully!")