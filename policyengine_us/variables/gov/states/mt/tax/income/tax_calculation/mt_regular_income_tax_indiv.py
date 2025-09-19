from policyengine_us.model_api import *


class mt_regular_income_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana income (subtracting capital gains before 2024) tax before refundable credits, when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.main
        taxable_income = person("mt_taxable_income_indiv", period)
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        if p.capital_gains.in_effect:
            capital_gains = person("long_term_capital_gains", period)
            taxable_income = max_(taxable_income - capital_gains, 0)
        return select_filing_status_value(filing_status, p, taxable_income)
