from policyengine_us.model_api import *


def create_remove_net_investment_tax() -> Reform:
    class net_investment_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Repeal of investment income tax"
        unit = USD
        documentation = "The repeal of investment income tax under the tax foundation growth and opportunity plan"
        definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.investment.net_investment_income_tax
        threshold = p.threshold[tax_unit("filing_status", period)]
        excess_agi = max_(
            0, tax_unit("adjusted_gross_income", period) - threshold
        )
        base = min_(
            max_(0, tax_unit("net_investment_income", period)),
            excess_agi,
        )
        if (
            parameters(
                period
            ).gov.contrib.tax_foundation.growth_and_opportunity.remove_net_investment_tax
            == True
        ):
            investment_income_tax = 0
        else:
            investment_income_tax = p.rate * base
        return investment_income_tax

    class reform(Reform):
        def apply(self):
            self.update_variable(net_investment_income_tax)

    return reform


def create_remove_net_investment_tax_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_net_investment_tax()

    p = parameters(period).gov.contrib.tax_foundation.growth_and_opportunity

    if p.remove_net_investment_tax == True:
        return create_remove_net_investment_tax()
    else:
        return None


remove_net_investment_income = create_remove_net_investment_tax_reform(
    None, None, bypass=True
)
