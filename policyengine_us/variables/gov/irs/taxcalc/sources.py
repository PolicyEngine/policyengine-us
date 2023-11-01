from policyengine_us.model_api import *


class k1bx14(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "Partner self-employment earnings/loss (included in e26270 total)"
    )
    unit = USD


class hasqdivltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = "Whether this tax unit has qualified dividend income, or long-term capital gains income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Negatives cannot offset other income sources
        INCOME_SOURCES = [
            "c01000",
            "c23650",
            "long_term_capital_gains",
            "non_sch_d_capital_gains",
            "qualified_dividend_income",
        ]
        return np.any(
            [
                add(tax_unit, period, [income_source]) > 0
                for income_source in INCOME_SOURCES
            ]
        )


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Net capital gains"
    unit = USD
    documentation = "Net capital gains (long and short term) before exclusion"

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            ["long_term_capital_gains", "short_term_capital_gains"],
        )
