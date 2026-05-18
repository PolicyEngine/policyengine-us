from policyengine_us.model_api import *


class ak_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alaska CCAP monthly benefit"
    definition_period = MONTH
    defined_for = "ak_ccap_eligible"
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=846",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203",
    )

    def formula(spm_unit, period):
        total_per_child = add(spm_unit, period, ["ak_ccap_benefit_per_child"])
        copay = spm_unit("ak_ccap_copay", period)
        return max_(0, total_per_child - copay)
