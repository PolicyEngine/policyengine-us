from policyengine_us.model_api import *


class sd_ssp_care_income_deductions(Variable):
    value_type = float
    entity = Person
    label = "Approved South Dakota SSP care income deductions"
    definition_period = MONTH
    unit = USD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06"
    documentation = "Verified statutory exclusions, eligible insurance premiums and dependent allocations. Nursing-facility-only personal needs allowances do not automatically apply."
