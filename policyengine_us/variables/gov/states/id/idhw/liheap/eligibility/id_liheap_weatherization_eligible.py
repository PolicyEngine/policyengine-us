from policyengine_us.model_api import *


class id_liheap_weatherization_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP weatherization program eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household meets Idaho LIHEAP weatherization income requirements (200% FPL)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83(b)",
    ]

    def formula(spm_unit, period, parameters):
        # Weatherization uses 200% Federal Poverty Level, not 60% SMI
        income = spm_unit("id_liheap_income", period)
        fpg_monthly = spm_unit("spm_unit_fpg", period.this_year) / 12

        # 200% of Federal Poverty Guidelines
        weatherization_income_limit = fpg_monthly * 2.0

        return income <= weatherization_income_limit
