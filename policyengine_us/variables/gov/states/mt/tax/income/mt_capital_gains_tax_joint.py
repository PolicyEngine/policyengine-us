from policyengine_us.model_api import *


class mt_capital_gains_tax_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana net long-term capital gains tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        capital_gains = person("long_term_capital_gains", period)
        taxable_income = person("mt_taxable_income_joint", period)
        nonqualified_income = max_(taxable_income - capital_gains, 0)
        p = parameters(period).gov.states.mt.tax.income.main.capital_gains
        filing_status = person.tax_unit("filing_status", period)
        gap = p.threshold[filing_status] - nonqualified_income
        lower_base_tax = (
            gap * p.rates.reduced_capital_gains.lower[filing_status]
        )
        capital_gains_under_threshold = capital_gains <= gap
        lower_capital_gains_tax = (
            capital_gains * p.rates.reduced_capital_gains.lower[filing_status]
        )
        higher_capital_gains_tax = (
            lower_base_tax
            + (capital_gains - gap)
            * p.rates.reduced_capital_gains.higher[filing_status]
        )
        reduced_capital_gains_tax = where(
            capital_gains_under_threshold,
            lower_capital_gains_tax,
            higher_capital_gains_tax,
        )
        nonqualified_income_over_threshold = gap < 0
        capital_gains_over_threshold = (
            capital_gains * p.rates.reduced_capital_gains.higher[filing_status]
        )
        capital_gains_tax = p.availability * where(
            nonqualified_income_over_threshold,
            capital_gains_over_threshold,
            reduced_capital_gains_tax,
        )
        return is_head * person.tax_unit.sum(capital_gains_tax)
