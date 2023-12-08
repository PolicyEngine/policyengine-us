from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter_credit
        gross_household_income = tax_unit("mt_gross_household_income", period)
        # Get net_household_income
        net_household_income = tax_unit(
            "mt_elderly_homeowner_or_renter_credit_net_household_income",
            period,
        )
        # Credit Computation
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        credit_amount = max_(
            rent * p.rent_equivalent_tax_rate
            + property_tax
            - net_household_income,
            0,
        )
        capped_credit = min_(credit_amount, p.cap)
        return p.multiplier.calc(gross_household_income) * capped_credit
