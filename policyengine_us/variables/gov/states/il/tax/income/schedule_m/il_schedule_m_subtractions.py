from policyengine_us.model_api import *


class il_schedule_m_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL Schedule M deductions"
    unit = USD
    documentation = (
        "Illinois Schedule M subtractions not modeled by other variables. "
        "Excludes the subtraction for restoring amounts held under a claim of "
        "right (line 15), which il_claim_of_right_subtraction computes."
    )
    definition_period = YEAR
    reference = "https://taxarchive.illinois.gov/content/dam/soi/en/web/taxarchive/forms/income-tax/2019/individual/il-1040-schedule-m.pdf"
    defined_for = StateCode.IL
