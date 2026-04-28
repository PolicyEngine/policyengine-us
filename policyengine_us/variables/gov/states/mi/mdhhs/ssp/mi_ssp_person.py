from policyengine_us.model_api import *


class mi_ssp_person(Variable):
    value_type = float
    entity = Person
    label = "Michigan State Supplementary Payment per person"
    unit = USD
    definition_period = MONTH
    defined_for = "mi_ssp_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )

    def formula(person, period, parameters):
        couple_eligible = person("mi_ssp_couple_eligible", period)
        return where(
            couple_eligible,
            person("mi_ssp_couple_amount", period),
            person("mi_ssp_individual_amount", period),
        )
