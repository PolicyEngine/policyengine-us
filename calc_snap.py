from policyengine_us import Simulation
import numpy as np

state_codes = {
    1: 'AL', 2: 'AK', 4: 'AZ', 5: 'AR', 6: 'CA',
    8: 'CO', 9: 'CT', 10: 'DE', 11: 'DC',
    12: 'FL', 13: 'GA', 15: 'HI', 16: 'ID', 17: 'IL',
    18: 'IN', 19: 'IA', 20: 'KS', 21: 'KY', 22: 'LA',
    23: 'ME', 24: 'MD', 25: 'MA', 26: 'MI', 27: 'MN',
    28: 'MS', 29: 'MO', 30: 'MT', 31: 'NE', 32: 'NV',
    33: 'NH', 34: 'NJ', 35: 'NM', 36: 'NY',
    37: 'NC', 38: 'ND', 39: 'OH', 40: 'OK', 41: 'OR',
    42: 'PA', 44: 'RI', 45: 'SC', 46: 'SD',
    47: 'TN', 48: 'TX', 49: 'UT', 50: 'VT', 51: 'VA',
    53: 'WA', 54: 'WV', 55: 'WI', 56: 'WY'
}

situation = {
    'people': {'person': {}},
    'tax_units': {'tax_unit': {'members': ['person']}},
    'families': {'family': {'members': ['person']}},
    'spm_units': {'spm_unit': {'members': ['person']}},
    'households': {'household': {'members': ['person']}}
}

print("State,SNAP Benefit")

for code, abbr in state_codes.items():
    try:
        sim = Simulation(start_instant='2025-01-01', situation=situation)
        sim.set_input('employment_income', 2025, [10000])
        sim.set_input('state_code', 2025, [code])
        snap = sim.calculate('snap', 2025)[0]
        print(f"{abbr},${snap:.2f}")
    except Exception as e:
        print(f"{abbr},Error: {str(e)[:50]}")
