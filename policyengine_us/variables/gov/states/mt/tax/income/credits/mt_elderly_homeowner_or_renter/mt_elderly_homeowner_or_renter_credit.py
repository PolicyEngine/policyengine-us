from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        gross_household_income = person(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            period,
        )
        # Get net_household_income and allocate it to the head
        head = person("is_tax_unit_head", period)
        net_household_income = add(
            person.tax_unit,
            period,
            ["mt_elderly_homeowner_or_renter_credit_net_household_income"],
        )
        # Credit Computation
        property_tax = add(person.tax_unit, period, ["real_estate_taxes"])
        rent = add(person.tax_unit, period, ["rent"])
        countable_rent = rent * p.rent_equivalent_tax_rate
        countable_rent_and_property_tax = property_tax + countable_rent
        uncapped_credit_unit = max_(
            countable_rent_and_property_tax - net_household_income, 0
        )
        uncapped_credit = uncapped_credit_unit * head
        capped_credit = min_(uncapped_credit, p.cap)
        multiplier = p.multiplier.calc(gross_household_income)
        return capped_credit * multiplier
