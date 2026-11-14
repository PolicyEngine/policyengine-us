from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.oh.dcy.ccap.oh_ccap_child_age_group import (
    OHCCAPAgeGroup,
)


class oh_ccvp_child_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = OHCCAPAgeGroup
    default_value = OHCCAPAgeGroup.PRESCHOOL
    definition_period = MONTH
    label = "Ohio Child Care Choice Voucher Program child age group"
    defined_for = StateCode.OH
    reference = "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_36.pdf#page=3"

    def formula(person, period, parameters):
        # Procedure Letter 36 prices a child enrolled in, or eligible to enroll in,
        # kindergarten at its school-age row, so a child past the five-year boundary
        # that oh_ccap_child_age_group uses takes that row whether or not the child
        # attends school, and so does a younger child already in school. The chart
        # has no summer row.
        p = parameters(period).gov.states.oh.dcy.ccap.age_group
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        base_group = p.months.calc(age_in_months)
        in_school = person("is_in_k12_school", period.this_year)
        school_age = (base_group == OHCCAPAgeGroup.SCHOOL_AGE.index) | (
            (base_group == OHCCAPAgeGroup.PRESCHOOL.index) & in_school
        )
        return select(
            [
                school_age,
                base_group == OHCCAPAgeGroup.INFANT.index,
                base_group == OHCCAPAgeGroup.TODDLER.index,
            ],
            [
                OHCCAPAgeGroup.SCHOOL_AGE,
                OHCCAPAgeGroup.INFANT,
                OHCCAPAgeGroup.TODDLER,
            ],
            default=OHCCAPAgeGroup.PRESCHOOL,
        )
