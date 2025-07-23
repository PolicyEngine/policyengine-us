from policyengine_us.model_api import *


class me_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine main income tax (before credits and supplemental tax)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("me_taxable_income", period)
        filing_status = tax_unit("filing_status", period)

        p = parameters(period).gov.states.me.tax.income.main

        return select_filing_status_value(filing_status, p, taxable_income)
