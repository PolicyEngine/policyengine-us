from policyengine_us.model_api import *


class az_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        income = tax_unit("az_taxable_income", period)
        filing_status = tax_unit("az_filing_status", period)
        p = parameters(period).gov.states.az.tax.income.main

        return select_filing_status_value(filing_status, p, income)
