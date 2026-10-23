from policyengine_us.model_api import *


class tax_unit_qualified_passenger_vehicle_loan_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit qualified passenger vehicle loan interest"
    unit = USD
    documentation = (
        "Qualified passenger vehicle loan interest on the tax unit's return, "
        "before the dollar limit and the modified adjusted gross income "
        "phase-out."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_B_i",
        "https://www.govinfo.gov/content/pkg/FR-2026-09-08/pdf/2026-18219.pdf#page=24",
        "https://www.govinfo.gov/content/pkg/FR-2026-09-08/pdf/2026-18219.pdf#page=28",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # 26 U.S.C. 163(h)(4)(B)(i) counts interest on indebtedness incurred
        # by the taxpayer: both spouses' loans on a joint return (26 CFR
        # 1.163-16(h)(3), Example 1), and not a dependent's loans.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        own_interest = tax_unit.sum(
            head_or_spouse
            * person("qualified_passenger_vehicle_loan_interest_person", period)
        )
        # A household-level amount does not say who incurred the loan. It
        # goes in full to the tax unit of the household head (the oldest
        # member when no head is designated), so it counts on one return.
        is_household_head = person("is_household_head", period)
        has_household_head = person.household.any(is_household_head)
        age = person("age", period)
        holds_household_amount = where(
            has_household_head,
            person.get_rank(person.household, -age, condition=is_household_head) == 0,
            person.get_rank(person.household, -age) == 0,
        )
        household_interest = person.household(
            "qualified_passenger_vehicle_loan_interest", period
        )
        return own_interest + tax_unit.sum(holds_household_amount * household_interest)
