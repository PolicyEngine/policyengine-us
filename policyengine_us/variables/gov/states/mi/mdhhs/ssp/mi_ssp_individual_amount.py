from policyengine_us.model_api import *


class mi_ssp_individual_amount(Variable):
    value_type = float
    entity = Person
    label = "Michigan SSP individual payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "mi_ssp_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )

    def formula(person, period, parameters):
        living_arrangement = person("mi_ssp_living_arrangement", period)
        p = parameters(period).gov.states.mi.mdhhs.ssp.payment
        return p.individual[living_arrangement]
