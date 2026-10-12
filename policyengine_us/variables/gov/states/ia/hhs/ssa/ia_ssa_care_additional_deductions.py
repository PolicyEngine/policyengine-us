from policyengine_us.model_api import *


class ia_ssa_care_additional_deductions(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved additional care income deductions"
    definition_period = MONTH
    unit = USD
    reference = ("https://hhs.iowa.gov/media/3987/download?inline=",)
    documentation = "Verified dependent/spouse allocations and unmet medical needs; for residential care also approved first-month community expenses and work-related deductions. Excludes the built-in maintenance allowance and general/ordinary earnings disregards."
