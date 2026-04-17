from policyengine_us.model_api import *


class ks_529_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.kansasstatetreasurer.ks.gov/learn_quest.html",
        "https://www.ksrevenue.gov/faqs-taxii.html",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.agi.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap[filing_status] * beneficiaries
        return min_(contributions, cap)
