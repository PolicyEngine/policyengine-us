from policyengine_us.model_api import *


class de_cdcc_indv(Variable):
    value_type = float
    entity = Person
    label = "Delaware CDCC per person for combined separate filing"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=10"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # PIT-RES Line 31: "the credit may only be applied against
        # the tax imposed on the spouse with the lower taxable
        # income reported on Line 23."  Locked to the lower-income
        # spouse's column under combined separate filing.
        # With equal taxable incomes either spouse has the lower income, so
        # the credit goes to the column with more tax left after that
        # spouse's aged credit (each column's own $110 personal credit is the
        # same), whichever spouse is labelled head.
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        person_taxable = person("de_taxable_income_indv", period)
        head_taxable = person.tax_unit.sum(is_head * person_taxable)
        spouse_taxable = person.tax_unit.sum(is_spouse * person_taxable)

        room = person(
            "de_income_tax_before_non_refundable_credits_indv", period
        ) - person("de_aged_personal_credit_indv", period)
        head_room = person.tax_unit.sum(is_head * room)
        spouse_room = person.tax_unit.sum(is_spouse * room)
        head_takes = (head_taxable < spouse_taxable) | (
            (head_taxable == spouse_taxable) & (head_room > spouse_room)
        )

        is_lower_income = (is_head & head_takes) | (is_spouse & ~head_takes)
        return is_lower_income * person.tax_unit("de_cdcc", period)
