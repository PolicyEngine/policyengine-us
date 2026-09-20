from policyengine_us.model_api import *


class tx_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Texas CCS eligible child"
    definition_period = MONTH
    reference = (
        "https://www.twc.texas.gov/sites/default/files/ogc/docs/rules-chapter-809-child-care-services-twc.pdf#page=30",
        "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-41",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        age_limit = where(is_disabled, p.disabled_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_status_eligible = person(
            "is_citizen_or_legal_immigrant", period.this_year
        )
        standard = age_eligible & is_dependent & immigration_status_eligible
        authorized = person("tx_ccs_dfps_authorized", period)
        court = person("is_under_court_supervision", period.this_year)
        # 809.41 expressly excludes 809.49 protective care from the general
        # conditions. Older court-supervised children require DFPS approval.
        protective_age = (age < p.child) | (
            (is_disabled | court) & (age < p.disabled_child)
        )
        return standard | (authorized & protective_age)
