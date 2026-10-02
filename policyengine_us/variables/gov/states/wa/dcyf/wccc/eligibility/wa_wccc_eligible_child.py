from policyengine_us.model_api import *


class wa_wccc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Washington WCCC"
    definition_period = MONTH
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0005",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.802",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.dcyf.wccc.eligibility.age_threshold
        age = person("monthly_age", period)
        # WAC 110-15-0005(3)(b)(ii)(A)-(B) and RCW 43.216.802(2)(a)(ii): a
        # child with a verified special need (WAC 110-15-0220(1); is_disabled
        # proxy) or under court supervision shares the higher age limit.
        is_disabled = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = (age < p.child) | (
            (is_disabled | court_supervision) & (age < p.special_needs_child)
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & is_dependent
