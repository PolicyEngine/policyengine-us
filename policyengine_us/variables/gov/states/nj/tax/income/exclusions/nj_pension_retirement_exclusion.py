from policyengine_us.model_api import *


class nj_pension_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Pension/Retirement Exclusion"
    unit = USD
    documentation = "New Jersey pension and retirement excludable amount if eligible (Line 28a)"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-10/",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        pension_income = add(tax_unit, period, ["nj_eligible_pension_income"])
        fraction = tax_unit("nj_retirement_exclusion_fraction", period)
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement
        filing_status = tax_unit("filing_status", period)
        return min_(pension_income * fraction, p.max_amount[filing_status])
