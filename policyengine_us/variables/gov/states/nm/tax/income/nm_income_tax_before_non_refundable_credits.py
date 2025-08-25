from policyengine_us.model_api import *


class nm_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income tax before non-refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        income = tax_unit("nm_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.nm.tax.income.main
        return select_filing_status_value(
            filing_status,
            p,
            income,
        )
