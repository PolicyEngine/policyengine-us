from policyengine_us.model_api import *


class snap_child_support_gross_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "SNAP child support payment deduction from gross income per person"
    unit = USD
    documentation = "Deduction for child support payments when computing SNAP gross income, calculated at person level with proration for ineligible members"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_4"

    def formula(person, period, parameters):
        child_support = person("child_support_expense", period)

        # Apply proration only for ineligible members
        is_prorate_person = person("is_snap_prorate_person", period.this_year)
        prorate_fraction = person.spm_unit(
            "snap_prorate_fraction", period.this_year
        )

        # Ineligible members get their income reduced by prorate_fraction
        prorate_exclusion = where(
            is_prorate_person, child_support * prorate_fraction, 0
        )

        child_support_after_proration = child_support - prorate_exclusion

        state = person.household("state_code_str", period)
        p = parameters(period).gov.usda.snap.income.deductions
        return p.child_support[state] * child_support_after_proration
