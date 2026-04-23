from policyengine_us.model_api import *


class ut_529_plan_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah 529 plan contribution tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://my529.org/utah-state-tax-benefits-information/",
        "https://incometax.utah.gov/credits/my529",
    )
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.income.credits.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap[filing_status] * beneficiaries
        eligible_contributions = min_(contributions, cap)
        return eligible_contributions * p.rate
