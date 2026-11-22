from policyengine_us.model_api import *


class dependent_care_employer_benefits_forfeited_or_carried_forward(Variable):
    value_type = float
    entity = Person
    label = "Dependent care benefits forfeited or carried forward to the next year"
    documentation = (
        "Form 2441 line 14 (FTB 3506 line 15): the part of this person's "
        "dependent_care_employer_benefits (line 12) that they did not "
        "receive this year, either forfeited because they did not incur the "
        "expense or carried forward to use in the next year. W-2 box 10 "
        "includes these amounts and box 1 leaves them out, as it leaves out "
        "all of line 12, so they are neither wages nor taxable dependent care "
        "benefits. Box 10 amounts above the plan's exclusion are box 1 wages, "
        "not line 12, and do not go here. On the 2021 to 2024 forms line 14 "
        "also takes amounts from line 13 (prior-year benefits used this year) "
        "that were forfeited or carried over, which the model does not "
        "include; enter only the part from line 12. Enter each person's own "
        "amount: it reduces only that person's line 12, and any amount beyond "
        "it, or a negative amount, counts as zero. An entry applies only to "
        "the year entered; a year without one uses zero. Because of its "
        "formula, Core does not count this as an input variable, so "
        "Simulation.to_input_dict() and to_input_dataframe() leave a supplied "
        "amount out unless include_computed_variables=True; supply it in the "
        "situation or with set_input."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = (
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
        # PDF pages 18-19. Box 10 reports amounts "regardless of any employee
        # forfeitures"; amounts "over your plan's exclusion" go in boxes 1, 3
        # and 5.
        "https://www.irs.gov/pub/irs-prior/iw2w3--2025.pdf#page=18",
    )

    def formula(person, period, parameters):
        # A formula stops Core carrying an entry into later years and uprating it.
        return person.empty_array()
