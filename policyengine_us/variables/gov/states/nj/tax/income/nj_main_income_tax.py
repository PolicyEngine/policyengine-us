from policyengine_us.model_api import *


class nj_main_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey income tax"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-2-1/"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("nj_taxable_income", period)
        filing_status = tax_unit("filing_status", period)

        # Get main nj tax parameter tree.
        p = parameters(period).gov.states.nj.tax.income.main

        return select_filing_status_value(
            filing_status,
            p,
            taxable_income,
        )
