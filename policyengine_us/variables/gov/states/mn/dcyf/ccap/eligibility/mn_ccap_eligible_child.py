from policyengine_us.model_api import *


class mn_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Minnesota CCAP"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.01 subd. 7 — eligible child (formerly 119B.011).
        "https://www.revisor.mn.gov/statutes/cite/142E.01",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # Under 13, or under 15 if the child has a disability.
        age_eligible = where(is_disabled, age < p.disabled_child, age < p.child)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible
