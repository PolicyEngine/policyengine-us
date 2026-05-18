from policyengine_us.model_api import *


class ak_ccap_special_needs_supplement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP special needs (Alaska IN!) supplement per child"
    definition_period = MONTH
    defined_for = "ak_ccap_child_eligible"
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=857",
        "https://health.alaska.gov/en/services/alaska-inclusive-child-care/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.special_needs
        is_disabled = person("is_disabled", period.this_year)
        authorized = person("ak_ccap_authorized_rate_per_child", period)
        # Per Manual §4370-2, the supplement is paid in addition to the
        # authorized reimbursement rate, up to (multiplier - 1) times that rate.
        return is_disabled * authorized * (p.supplement_multiplier - 1)
