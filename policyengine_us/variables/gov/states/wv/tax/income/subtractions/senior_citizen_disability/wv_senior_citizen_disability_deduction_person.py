from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "West Virginia senior citizen or disability deduction for each person"
    unit = USD
    documentation = (
        "Up to $8,000 of an eligible person's own federal adjusted gross "
        "income, less their overlapping modifications. On a joint return "
        "each spouse's federal AGI is their part of the joint return's AGI "
        "(adjusted_gross_income_person), as in Schedule M's separate columns. "
        "W. Va. Code 11-21-12(f) recomputes each spouse's federal AGI as if "
        "they had filed separate federal returns only when spouses who filed "
        "a joint federal return file separate West Virginia returns. "
        "PolicyEngine uses the federal filing status for West Virginia, so it "
        "does not model that case."
    )
    definition_period = YEAR
    reference = (
        # Subsections (c)(9) and (f).
        "https://code.wvlegislature.gov/11-21-12/",
        # Schedule M, line 47: "Joint income must be divided between spouses
        # with regard to their respective percentage of ownership."
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=29",
        # Filing status: "When joint federal but separate state returns are
        # filed, each spouse must report his/her federal adjusted gross
        # income separately as if the federal adjusted gross income of each
        # had been determined on separately filed federal returns."
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=21",
    )
    defined_for = "wv_senior_citizen_disability_deduction_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        agi_person = person("adjusted_gross_income_person", period)
        capped_agi = min_(p.cap, agi_person)
        # While the legal code specifies that the total value of the modifications can not exceed
        # a certain amount, we can mathematically derive this condition by subtracting the modification
        # amount from the adjusted gross income as specified in subdivision (c) (9) (ii)
        total_modifications = person(
            "wv_senior_citizen_disability_deduction_total_modifications",
            period,
        )
        return max_(0, capped_agi - total_modifications)
