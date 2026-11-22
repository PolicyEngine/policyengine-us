from policyengine_us.model_api import *


class taxable_dependent_care_benefits_reported(Variable):
    value_type = float
    entity = Person
    label = "Reported taxable dependent care benefits"
    documentation = (
        "This person's part of Form 2441 line 26, taxable dependent care "
        "benefits (Form 1040 line 1e from 2022), as supplied, for returns the "
        "model does not compute: grace-period carryovers used (line 13), a "
        "plan maximum below the statutory cap (line 21), or the 2021 and "
        "2022 relief rules. An amount of zero or more is used as entered, "
        "including zero. A negative amount, such as the default -1, means "
        "not supplied: taxable_dependent_care_benefits then uses this "
        "person's computed share of line 26, whatever other people report. "
        "The amount changes only taxable_dependent_care_benefits and its "
        "readers; the exclusion (dependent_care_assistance_exclusion, line "
        "25) and the child and dependent care credit stay computed, though "
        "the credit's rate follows adjusted gross income, which includes the "
        "supplied amount. On a joint return, a spouse without a supplied "
        "amount keeps their computed share, so supply an amount for each "
        "spouse with benefits, the amounts adding to line 26. An entry "
        "applies only to the year entered. Because of its formula, Core does "
        "not count this as an input variable, so Simulation.to_input_dict() "
        "and to_input_dataframe() leave a supplied amount out unless "
        "include_computed_variables=True; supply it in the situation or with "
        "set_input."
    )
    unit = USD
    definition_period = YEAR
    default_value = -1
    reference = (
        # Line 26: "Taxable benefits. Subtract line 25 from line 23."
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
        # Line 26: "Enter this amount on Form 1040, 1040-SR, or 1040-NR, line 1e."
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=6",
    )

    def formula(person, period, parameters):
        # A formula stops Core carrying an entry into later years and uprating it.
        return person.empty_array() - 1
