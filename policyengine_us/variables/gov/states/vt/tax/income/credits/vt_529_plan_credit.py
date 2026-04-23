from policyengine_us.model_api import *


class vt_529_plan_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont 529 plan contribution tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/individuals/personal-income-tax/tax-credits",
        "https://vt529.org/benefits",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        eligible_contributions = min_(contributions, cap)
        return eligible_contributions * p.rate
