from policyengine_us.model_api import *


class mt_elderly_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Check eligibility based on state, rent, filing status, and income.
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_renter_credit
        age_head = tax_unit("age_head", period)
        gross_household_income = tax_unit("mt_gross_household_income", period)
        eligibility = (age_head >= p.age_min) & (
            gross_household_income < p.income_max
        )

        # Calculate net_household_income
        standard_exclusion = p.standard_exclusion
        temp1 = max_(gross_household_income - standard_exclusion, 0)
        net_household_income = p.household_income_reduction.calc(temp1) * temp1

        # Credit Computation
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        rate = p.rate
        cap = p.cap
        temp2 = max_(rent * rate + property_tax - net_household_income, 0)
        temp3 = min_(temp2, cap)
        total = p.credit_multiplier.calc(gross_household_income) * temp3
        return eligibility * total
