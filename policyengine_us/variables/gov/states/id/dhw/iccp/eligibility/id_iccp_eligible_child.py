from policyengine_us.model_api import *


class id_iccp_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Child eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://files.dfm.idaho.gov/dfm-admin-website/rules/current/16/160612.pdf#page=12"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.age_threshold
        age = person("age", period.this_year)
        # IDAPA 16.06.12.105.03: a child under 13 is eligible; a child may be
        # eligible until the month of their 19th birthday if (a) physically or
        # mentally incapable of self-care (is_disabled proxies the licensed
        # practitioner's verification) or (b) "a court order, probation order,
        # child protection, or mental health case plan requires constant
        # supervision". We treat the constant-supervision content of the order
        # as a verification detail and use the single court-supervision input.
        # The birthday-month cutoff is approximated with annual age, and the
        # discretionary "may be eligible" wording is modeled as eligible.
        is_disabled = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = (age < p.child) | (
            (is_disabled | court_supervision) & (age < p.disabled_child)
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
