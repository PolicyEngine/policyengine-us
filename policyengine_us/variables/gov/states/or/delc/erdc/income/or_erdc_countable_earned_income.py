from policyengine_us.model_api import *


class or_erdc_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Oregon ERDC countable earned income"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0035"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc
        earned = add(person, period, p.income.countable_income.earned_sources)
        # OAR 414-175-0015(2)(d) keeps unmarried children under 18, and
        # 18-year-old secondary students, in the filing group as children, and
        # OAR 414-175-0035(21)(a) excludes a child's earned income. We don't
        # track half-time attendance at the moment, so any 18-year-old
        # secondary student counts as a child.
        age = person("age", period.this_year)
        child_age_limit = p.age_threshold.filing_group_child
        is_secondary_student = person("is_in_secondary_school", period.this_year)
        is_filing_group_child = (age < child_age_limit) | (
            (age < child_age_limit + 1) & is_secondary_student
        )
        # Earned income is counted only from caretakers (tax unit heads and
        # spouses), never from a filing-group child that age-based headship
        # would otherwise treat as a spouse.
        caretaker = (
            person("is_tax_unit_head_or_spouse", period.this_year)
            & ~is_filing_group_child
        )
        return earned * caretaker
