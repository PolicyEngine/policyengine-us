from policyengine_us.model_api import *


class ga_investment_in_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia investment in 529 plan deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet",
        "https://rules.sos.ga.gov/gac/560-7-4-.04",
        "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=23",  # Path2College 529 deduction - $4,000 per beneficiary
    )
    defined_for = StateCode.GA
