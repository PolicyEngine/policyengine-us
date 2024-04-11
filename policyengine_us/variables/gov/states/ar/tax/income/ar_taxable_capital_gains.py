from policyengine_us.model_api import *


class ar_taxable_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Arkansas taxable capital gains"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        long_term_capital_gains = person("long_term_capital_gains", period)
        short_term_capital_gains = person("short_term_capital_gains", period)
        p = parameters(
            period
        ).gov.states.ar.tax.income.gross_income.capital_gains
        taxable_long_term_capital_gains = long_term_capital_gains * (
            1 - p.exempt_rate
        )
        return short_term_capital_gains + taxable_long_term_capital_gains
