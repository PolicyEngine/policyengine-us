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
        nonqualified_income = taxable_income - capital_gains
        p = parameters(
            period
        ).gov.states.mt.tax.income.main.capital_gains_tax_rate
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        difference = p.threshold[filing_status] - nonqualified_income
        tax_nonqualified_income_below_threshold = where(
            capital_gains <= difference,
            p.active_status
            * capital_gains
            * p.rate_below_threshold_income_difference[filing_status],
            p.active_status
            * (
                difference
                * p.rate_below_threshold_income_difference[filing_status]
                + (capital_gains - difference)
                * p.rate_above_threshold_income_difference[filing_status]
            ),
        )
        return where(
            difference < 0,
            p.active_status
            * capital_gains
            * p.rate_above_threshold[filing_status],
            tax_nonqualified_income_below_threshold,
        )
