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
        age_eligible = age < p.child
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & is_dependent
