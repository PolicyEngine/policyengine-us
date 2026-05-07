from policyengine_us.model_api import *


class ak_resides_in_assisted_living_home(Variable):
    value_type = bool
    entity = Person
    label = "Resides in an Alaska assisted living home"
    definition_period = YEAR
    defined_for = StateCode.AK
    default_value = False
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=830",
        "https://health.alaska.gov/en/services/assisted-living-licensing-and-renewals/",
        "https://www.akleg.gov/statutesPDF/Title-47.pdf#page=310",
    )
