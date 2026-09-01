from policyengine_us.model_api import *


class or_erdc_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Oregon ERDC"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0022",
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0021",
    )

    def formula(person, period, parameters):
        p_erdc = parameters(period).gov.states["or"].delc.erdc
        p = p_erdc.age_threshold
        age = person("age", period.this_year)
        # OAR 414-175-0022(2)(b): disability covers the high-needs-rate
        # pathway in (2)(b)(D); court supervision under (2)(b)(B) and
        # compromised-safety circumstances under (2)(b)(E) are not tracked
        # at the moment.
        special_circumstances = (
            person("is_incapable_of_self_care", period.this_year)
            | person("is_in_foster_care", period)
            | person("is_disabled", period.this_year)
        )
        age_eligible = (age < p.child) | (
            (age < p.special_circumstances_child) & special_circumstances
        )
        # OAR 414-175-0021 requires a citizenship or qualified-noncitizen
        # status only "until May 1, 2024"; from that date DELC serves
        # children regardless of immigration status with state funds.
        immigration_eligible = where(
            p_erdc.immigration_test_in_effect,
            person("is_ccdf_immigration_eligible_child", period.this_year),
            True,
        )
        return age_eligible & immigration_eligible
