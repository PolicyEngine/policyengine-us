from policyengine_us.model_api import *


def create_rent_relief_tax_credit() -> Reform:
    class rent_relief_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rent Relief Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.congress.gov/bill/116th-congress/senate-bill/1106/text"

        def formula(tax_unit, period, parameters):

            # The applicable rent amount is capped at fair market rent
            rent = add(tax_unit, period, ["rent"])
            p = parameters(
                period
            ).gov.contrib.harris.rent_relief_act.rent_relief_credit
            safmr = tax_unit.household("small_area_fair_market_rent", period)
            safmr_used_for_hcv = tax_unit.household(
                "safmr_used_for_hcv", period
            )
            gross_income = add(tax_unit, period, ["irs_gross_income"])
            applicable_gross_income = where(
                safmr_used_for_hcv,
                gross_income + p.safmr_increase,
                gross_income,
            )
            capped_rent = min_(rent, safmr)
            gross_income_fraction = (
                p.gross_income_rate * applicable_gross_income
            )
            rent_excess = max_(capped_rent - gross_income_fraction, 0)
            applicable_percentage = p.applicable_percentage.calc(gross_income)
            return applicable_percentage * rent_excess

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            rent_relief_credit = tax_unit("rent_relief_tax_credit", period)
            return rent_relief_credit + previous_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(rent_relief_tax_credit)
            self.update_variable(income_tax_refundable_credits)

    return reform


def create_rent_relief_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_rent_relief_tax_credit()

    p = parameters(
        period
    ).gov.contrib.harris.rent_relief_act.rent_relief_credit

    if p.in_effect:
        return create_rent_relief_tax_credit()
    else:
        return None


rent_relief_tax_credit = create_rent_relief_tax_credit_reform(
    None, None, bypass=True
)
