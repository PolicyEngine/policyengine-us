from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class ny_main_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY main income tax (before credits and supplemental tax)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ny_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        rates = parameters(period).gov.states.ny.tax.income.main

        return select_filing_status_value(filing_status, rates, taxable_income)
