from policyengine_us.model_api import *


class wv_senior_citizen_disability_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "West Virginia senior citizen or disability deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-12/",
        "https://code.wvlegislature.gov/11-21-12a/",
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=6",
        "https://tax.wv.gov/Documents/PIT/2024/it140.PersonalIncomeTaxFormsAndInstructions.2024.pdf#page=6",
        "https://tax.wv.gov/Documents/TaxForms/2018/it140.booklet.pdf#page=5",
    )
    defined_for = "wv_senior_citizen_disability_deduction_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.senior_citizen_disability_deduction

        agi_person = person("adjusted_gross_income_person", period)
        # Box (c) excludes the person's own modified income receipts on
        # lines 35-46 before applying the cap. The separate section 12a
        # deduction for 529 contribution payments does not exclude income.
        excluded_amounts = add(person, period, p.excluded_income_sources)
        capped_income = min_(p.cap, agi_person - excluded_amounts)
        # Box (d) then subtracts the person's own lines 29-34 modifications.
        total_modifications = person(
            "wv_senior_citizen_disability_deduction_total_modifications",
            period,
        )
        return max_(0, capped_income - total_modifications)
