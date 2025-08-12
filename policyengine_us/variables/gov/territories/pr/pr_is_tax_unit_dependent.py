from policyengine_us.model_api import *


class pr_is_tax_unit_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico tax unit dependent"
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=28"

    def formula(person, period, parameters):
        # dependent definition in Puerto Rico:
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions.dependent.age_threshold
        age = person("age", period)

        # taxpayer is <21 years old OR >= 65 years old
        age_eligible = (age < p.younger) | (age >= p.older)

        # OR the taxpayer's mother or father
        parent_eligible = person("is_parent_of_filer_or_spouse", period)

        # OR a person over 21 that is incapable of self-support because of a physical or mental condition
        incapable_of_self_support_eligible = person(
            "is_incapable_of_self_care", period
        )

        is_blind = person("is_blind", period)

        # OR a university student <26 years old that attended at least 1 years of an accredited uni
        student_eligible = (person("is_full_time_college_student", period)) & (
            age < p.student
        )
        return (
            student_eligible
            | parent_eligible
            | incapable_of_self_support_eligible
            | is_blind
            | age_eligible
        )
