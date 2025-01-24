from policyengine_us.model_api import *


class state_sales_tax_income_bracket(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "State Sales Tax Income Bracket"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table
        income = add(tax_unit, period, p.income_sources)
        return p.income_bracket.calc(income)
