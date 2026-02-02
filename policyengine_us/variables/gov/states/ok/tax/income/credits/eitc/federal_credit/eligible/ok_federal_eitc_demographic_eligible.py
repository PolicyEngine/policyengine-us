from policyengine_us.model_api import *


class ok_federal_eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for EITC for the Oklahoma EITC computation"
    definition_period = YEAR
    reference = (
        # Oklahoma Statutes 68 O.S. Section 2357.43
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
    )
    defined_for = StateCode.OK
    documentation = """
    Demographic eligibility for EITC using FROZEN 2020 parameters.

    Tax units are demographically eligible if:
    1. They have qualifying children, OR
    2. At least one filer meets age requirements (without children)

    2020 Age requirements (for filers without qualifying children):
    - Minimum age: 25 (or 19 if full-time student)
    - Maximum age: 64

    Note: If the tax unit has qualifying children, age requirements
    do not apply to the filers.
    """

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # If tax unit has qualifying children, automatically eligible
        has_child = tax_unit("eitc_child_count", period) > 0
        age = person("age", period)
        # Use FROZEN 2020 age parameters per Oklahoma statute
        min_age_non_student = (
            parameters.gov.irs.credits.eitc.eligibility.age.min("2020-01-01")
        )
        min_age_student = (
            parameters.gov.irs.credits.eitc.eligibility.age.min_student(
                "2020-01-01"
            )
        )
        student = person("is_full_time_student", period)
        # Students have a lower minimum age requirement
        min_age = where(student, min_age_student, min_age_non_student)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(
            "2020-01-01"
        )
        # Check if at least one filer meets age requirements
        meets_age_requirements = (age >= min_age) & (age <= max_age)
        return has_child | tax_unit.any(meets_age_requirements)
