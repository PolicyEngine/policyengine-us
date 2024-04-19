from policyengine_us.model_api import *


class mt_capital_gains_tax_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana net long-term capital gains tax when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        capital_gains = person("long_term_capital_gains", period)
        taxable_income = person("mt_taxable_income_indiv", period)
        nonqualified_income = max_(taxable_income - capital_gains, 0)
        p = parameters(period).gov.states.mt.tax.income.main.capital_gains
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
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
        return p.availability * where(
            nonqualified_income_over_threshold,
            capital_gains_over_threshold,
            reduced_capital_gains_tax,
        )
