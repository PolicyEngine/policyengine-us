from policyengine_us.model_api import *


class mt_regular_income_tax_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income (subtracting capital gains since 2024) tax before refundable credits, when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main
        taxable_income = add(tax_unit, period, ["mt_taxable_income_joint"])
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        if p.capital_gains.in_effect:
            capital_gains = add(tax_unit, period, ["long_term_capital_gains"])
            taxable_income = max_(taxable_income - capital_gains, 0)
        return select_filing_status_value(
            filing_status,
            p,
            taxable_income,
        )
