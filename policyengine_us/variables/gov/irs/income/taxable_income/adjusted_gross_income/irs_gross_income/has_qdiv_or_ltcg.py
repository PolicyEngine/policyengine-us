from policyengine_us.model_api import *


class has_qdiv_or_ltcg(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has qualified dividends or long-term capital gains"
    documentation = "Whether this tax unit has qualified dividend income or long-term capital gains income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # negatives amounts cannot offset other income sources
        INCOME_SOURCES = [
            "loss_limited_net_capital_gains",
            "net_capital_gains",
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
