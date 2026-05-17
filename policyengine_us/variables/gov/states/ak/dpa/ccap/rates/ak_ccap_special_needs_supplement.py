from policyengine_us.model_api import *


class ak_ccap_special_needs_supplement(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Alaska CCAP special needs (Alaska IN!) supplemental rate per child"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = (
        "https://casetext.com/regulation/alaska-administrative-code/title-7-health-and-social-services/part-1-administration/chapter-41-child-care-assistance-program/section-7-aac-41060-children-with-special-needs",
        "https://health.alaska.gov/en/services/alaska-inclusive-child-care/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.special_needs
        is_disabled = person("is_disabled", period.this_year)
        is_child_eligible = person("ak_ccap_child_eligible", period)
        base_rate = person("ak_ccap_max_provider_rate_per_child", period)
        # Alaska IN! supplement goes up to (multiplier - 1)x the standard rate
        # in addition to the base rate, so the combined cap is multiplier * base.
        supplement_cap = base_rate * (p.supplement_multiplier - 1)
        return where(is_disabled & is_child_eligible, supplement_cap, 0)
