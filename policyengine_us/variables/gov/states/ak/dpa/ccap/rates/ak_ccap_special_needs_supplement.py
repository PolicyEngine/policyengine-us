from policyengine_us.model_api import *


class ak_ccap_special_needs_supplement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP maximum special-needs (Alaska IN!) supplement per child"
    documentation = "Maximum allowable per-child special-needs supplement under 7 AAC 41.060(b). Actual supplement amounts can be lower because the per-case CC51 authorization (a percentage between 0% and 100% of the authorized rate) is not observed; we apply the full cap to every disabled child."
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=858",
        "https://health.alaska.gov/en/services/alaska-inclusive-child-care/",
    )

    def formula(person, period, parameters):
        # We don't track the per-child CC51 supplement percentage at the
        # moment — apply the 7 AAC 41.060(b) cap (100% of authorized) to
        # every disabled child. `is_disabled` is narrower than Alaska IN!'s
        # "diagnosed special need" eligibility criterion.
        p = parameters(period).gov.states.ak.dpa.ccap.special_needs
        is_disabled = person("is_disabled", period.this_year)
        authorized = person("ak_ccap_authorized_rate_per_child", period)
        return is_disabled * authorized * (p.supplement_multiplier - 1)
