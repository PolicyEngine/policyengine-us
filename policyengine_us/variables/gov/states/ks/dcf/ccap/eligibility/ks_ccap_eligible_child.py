from policyengine_us.model_api import *


class ks_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Kansas CCAP"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm2810.htm"

    def formula(person, period, parameters):
        # KEESM 2810 permits ages 13-18 when incapable of self-care or under
        # court supervision. Eligibility-period extensions after the ordinary
        # age cutoff remain unmodeled.
        p = parameters(period).gov.states.ks.dcf.ccap.eligibility
        age = person("age", period.this_year)
        has_special_needs = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = where(
            has_special_needs | under_court_supervision,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
