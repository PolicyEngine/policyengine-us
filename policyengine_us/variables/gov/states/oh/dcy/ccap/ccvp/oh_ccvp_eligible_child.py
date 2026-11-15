from policyengine_us.model_api import *


class oh_ccvp_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Ohio Child Care Choice Voucher Program"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = "https://dam.assets.ohio.gov/image/upload/childrenandyouth.ohio.gov/For%20Partners/Rules%20and%20Resources/2025/PL_36.pdf#page=3"

    def formula(person, period, parameters):
        # Procedure Letter 36 prices school-age children under 15, or under 18
        # with special needs, and requires families to meet the other Publicly
        # Funded Child Care conditions, which include the child's immigration
        # status.
        p = parameters(period).gov.states.oh.dcy.ccap
        age = person("age", period.this_year)
        age_eligible = where(
            person("oh_ccap_special_needs", period),
            age < p.eligibility.special_needs_child_age_limit,
            age < p.ccvp.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
