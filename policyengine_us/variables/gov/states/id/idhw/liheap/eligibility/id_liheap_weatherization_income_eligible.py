from policyengine_us.model_api import *


class id_liheap_weatherization_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP weatherization income eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household meets income requirements for weatherization (200% FPL)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83",
    ]

    def formula(spm_unit, period, parameters):
        # Weatherization uses 200% FPL instead of 60% SMI
        income = spm_unit("id_liheap_income", period)

        # Get annual FPL and convert to monthly 200% FPL
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        monthly_limit = fpg * 2.0 / 12

        return income <= monthly_limit
