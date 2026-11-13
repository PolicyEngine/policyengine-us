from policyengine_us.model_api import *


class ok_ssp_ineligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma SSP ineligible child"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-2",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-6",
    )
    documentation = (
        "An SSI-ineligible child whom Oklahoma also counts: younger than 18 "
        "and not blind or disabled. Oklahoma gives no allocation for an "
        "older student."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ssp
        # OAC 340:15-1-2 excludes blind and disabled children regardless
        # of whether their immigration status permits SSI eligibility.
        younger = person("age", period.this_year) < p.ineligible_child_age_limit
        return (
            person("is_ssi_ineligible_child", period)
            & younger
            & ~person("is_ssi_aged_blind_disabled", period.this_year)
        )
