from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ny_ssp_is_minor(Variable):
    value_type = bool
    entity = Person
    label = "Minor for New York State Supplement Program living arrangements"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        # 18 NYCRR 398-2.1(t)
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-398-2.1",
        # Social Services Law 209(3)(b)
        "https://www.nysenate.gov/legislation/laws/SOS/209",
    )
    documentation = """
    A minor is below the minor age, or below the student minor age and a
    full-time student, and is neither married nor the head of a household.
    Set is_household_head for a student who lives away from home and heads
    their own household. Part-time attendance that counts as regular
    attendance under 20 CFR 416.1861 is not captured by is_full_time_student.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.otda.ssp
        age = person("age", period)
        student = person("is_full_time_student", period)
        # Marriage uses the SSI spouse test, so a child of a married couple
        # is not treated as married.
        married = _ssi_spouse_index(person, period) >= 0
        head = person("is_household_head", period)
        under_age = (age < p.minor_age) | ((age < p.student_minor_age) & student)
        return under_age & ~married & ~head
