"""
Configuration for uprating metadata detection.

This module defines which parameters are excluded from uprating detection checks.
Exclusions are typically for uprating SOURCE data (like CPI indices) rather than
parameters that should be uprated.
"""

# Parameters excluded from uprating detection
# Add file paths or directory patterns here
EXCLUSIONS = [
    # CPI indices - these ARE the uprating sources, not parameters to uprate
    "gov/bls/cpi",
    # Other uprating indices and factors
    "gov/hhs/uprating.yaml",  # HHS uprating factors
    "gov/ssa/nawi.yaml",  # National Average Wage Index (used for SS uprating)
    "gov/ssa/uprating.yaml", # SSA uprating factors
    # ACA benchmark premium uprating - this is already an uprating file
    "gov/aca/benchmark_premium_uprating.yaml",
    # Calibration data - not policy parameters
    "calibration/",
    # Contributed reforms - not policy parameters
    "contrib/",
    # New Jersey EITC match - updated mechanically each year
    "gov/states/nj/tax/income/credits/eitc/match.yaml",
    # Georgia retirement exclusion - updated mechanically each year
    "gov/states/ga/tax/income/agi/exclusions/retirement/cap/younger.yaml",
    # TANF is not adjusted with Inflation
    "gov/states/tx/tanf/",
    "gov/states/dc/dhs/tanf/",
    # Takeup is not adjusted with Inflation
    "gov/usda/snap/uprating.yaml",
    "gov/usda/wic/takeup.yaml",
    # Massachusetts SSP payment amount - updating schedule is not tied to CPI
    "gov/states/ma/dta/ssp/",
    # Fair Market Rent - adjustments reflect local rent inflation, not CPI
    "gov/states/vt/tax/income/credits/renter/",
    # Illinois AABD - not tied to CPI
    "gov/states/il/dhs/aabd/",
    # Colorado SSA programs are not adjusted with Inflation
    "gov/states/co/ssa/",
    # Age thresholds are not adjusted with Inflation
    "gov/states/ca/foster_care/age_threshold.yaml",
]

# Growth rate thresholds for detecting inflation-like updates
MIN_GROWTH_RATE = 0.0  # 0% - values should not decrease
MAX_GROWTH_RATE = 0.10  # 10% - filter out large policy changes
