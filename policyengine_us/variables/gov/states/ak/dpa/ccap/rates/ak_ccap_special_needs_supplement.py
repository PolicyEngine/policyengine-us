from policyengine_us.model_api import *


class ak_ccap_special_needs_supplement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP special needs (Alaska IN!) supplement per child"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=858",
        "https://health.alaska.gov/en/services/alaska-inclusive-child-care/",
    )

    def formula(person, period, parameters):
        # Per Manual §4370-2 ¶3, the Alaska IN! supplement is set per child
        # in increments of ten percent (10%) via an Alaska IN! Authorization
        # (form CC51), up to the 7 AAC 41.060(b) cap of 100% of the
        # authorized unit of care. We don't track the per-child CC51
        # determination at the moment, so we apply the regulatory maximum
        # — supplement = 1 x authorized (i.e., multiplier - 1 = 1) — for
        # every disabled eligible child, which over-estimates families whose
        # actual CC51 supplement is below the cap.
        p = parameters(period).gov.states.ak.dpa.ccap.special_needs
        is_disabled = person("is_disabled", period.this_year)
        authorized = person("ak_ccap_authorized_rate_per_child", period)
        return is_disabled * authorized * (p.supplement_multiplier - 1)
