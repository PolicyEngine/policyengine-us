from policyengine_us.model_api import *


class id_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP household gross monthly income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = (
        "Gross monthly income for Idaho LIHEAP eligibility determination"
    )
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.85",
    ]

    def formula(spm_unit, period, parameters):
        # Calculate monthly income from employment and other sources
        # Employment income is annual, so divide by 12
        employment = add(spm_unit, period, ["employment_income"]) / 12
        self_employment = (
            add(spm_unit, period, ["self_employment_income"]) / 12
        )

        # These are already monthly
        social_security = add(spm_unit, period, ["social_security"])
        ssi = add(spm_unit, period, ["ssi"])

        # Return total monthly income
        return employment + self_employment + social_security + ssi
