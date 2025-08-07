from policyengine_us.model_api import *


class ok_federal_eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit("eitc_child_count", period) > 0
        age = person("age", period)
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        min_age_non_student = (
            parameters.gov.irs.credits.eitc.eligibility.age.min(f"2020-01-01")
        )
        min_age_student = (
            parameters.gov.irs.credits.eitc.eligibility.age.min_student(
                f"2020-01-01"
            )
        )
        student = person("is_full_time_student", period)
        min_age = where(student, min_age_student, min_age_non_student)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(
            f"2020-01-01"
        )
        meets_age_requirements = (age >= min_age) & (age <= max_age)
        return has_child | tax_unit.any(meets_age_requirements)
