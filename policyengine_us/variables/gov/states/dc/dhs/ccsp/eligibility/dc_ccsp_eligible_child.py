from policyengine_us.model_api import *


class dc_ccsp_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for DC Child Care Subsidy Program (CCSP)"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = (
        "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8",
        "https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/CCDF%20FFY%202025-2027%20For%20District%20of%20Columbia.pdf#page=18",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.ccsp.age_threshold
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period)
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(is_disabled | court_supervision, p.disabled_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_status_eligible = person(
            "dc_ccsp_immigration_status_eligible_person", period
        )

        return age_eligible & is_dependent & immigration_status_eligible
