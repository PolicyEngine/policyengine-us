from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit(Variable):
    value_type = float
    entity = Person
    label = "Montana Elderly Homeowner/Renter Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_elderly_homeowner_or_renter_credit_eligible"
    reference = (
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # 2024 Form 2, Schedule 2EC
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # § 15-30-2337(4) defines gross household income as "all income
        # received by all individuals of a household", including members
        # outside the claimant's return (2024 Schedule 2EC line 17), so the
        # multiplier phase-out applies to the household's total income rather
        # than each person's share.
        gross_household_income = add(
            person.household,
            period,
            ["mt_elderly_homeowner_or_renter_credit_gross_household_income"],
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
