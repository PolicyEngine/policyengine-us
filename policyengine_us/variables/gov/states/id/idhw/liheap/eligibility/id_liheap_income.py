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
        # Use IRS gross income (like other LIHEAP implementations) and convert to monthly
        annual_income = add(spm_unit, period.this_year, ["irs_gross_income"])
        return annual_income / 12
