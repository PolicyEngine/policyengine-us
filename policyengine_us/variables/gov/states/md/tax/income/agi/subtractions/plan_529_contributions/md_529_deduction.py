from policyengine_us.model_api import *


class md_529_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland 529 plan contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-208&enession=2024RS",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=15",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.md.tax.income.agi.subtractions.plan_529_contributions
        contributions = tax_unit("investment_in_529_plan", period)
        beneficiaries = add(tax_unit, period, ["count_529_contribution_beneficiaries"])
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status] * max_(beneficiaries, 1)
        return min_(contributions, cap)
