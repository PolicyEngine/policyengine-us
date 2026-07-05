from policyengine_us.model_api import *


class nj_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-2-4/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income
        main_income_tax = tax_unit("nj_main_income_tax", period)
        non_refundable_credits = tax_unit("nj_non_refundable_credits", period)
        tax = max_(main_income_tax - non_refundable_credits, 0)
        # N.J.S.A. 54A:2-4 imposes no tax on filers with gross income at or
        # below the filing threshold.
        agi = tax_unit("nj_agi", period)
        filing_status = tax_unit("filing_status", period)
        return where(agi <= p.filing_threshold[filing_status], 0, tax)
