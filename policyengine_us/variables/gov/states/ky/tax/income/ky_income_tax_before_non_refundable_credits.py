from policyengine_us.model_api import *


class ky_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("ky_files_separately", period)
        taxable_income = where(
            filing_separately,
            add(tax_unit, period, ["ky_taxable_income_indiv"]),
            add(tax_unit, period, ["ky_taxable_income_joint"]),
        )
        p = parameters(period).gov.states.ky.tax.income
        return taxable_income * p.rate
