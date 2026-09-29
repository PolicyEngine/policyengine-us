from policyengine_us.model_api import *


class eitc_relevant_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "EITC-relevant investment income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#i_2",
        "https://www.irs.gov/pub/irs-prior/p596--2021.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        # Publication 596 Worksheet 1 keeps portfolio income, net capital
        # gains, and net passive income in separate baskets. A loss in one
        # basket cannot offset positive income in another.
        portfolio_income = add(
            tax_unit,
            period,
            [
                "taxable_interest_income",
                "tax_exempt_interest_income",
                "dividend_income",
            ],
        )
        capital_gains = add(
            tax_unit, period, ["net_capital_gains", "non_sch_d_capital_gains"]
        )
        # The model's undifferentiated rental input is treated as passive
        # rental income, consistently with its NIIT income mapping. Net the
        # passive amounts across the tax unit before applying the zero floor.
        passive_income = add(
            tax_unit, period, ["rental_income", "passive_partnership_s_corp_income"]
        )
        return portfolio_income + max_(0, capital_gains) + max_(0, passive_income)
