from policyengine_us.model_api import *


class medicaid_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrolled"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0025.pdf#page=4",
    )
    defined_for = "is_medicaid_eligible"

    def formula(person, period, parameters):
        takes_up = person("takes_up_medicaid_if_eligible", period)
        retained_chip = person(
            "ri_chip_postpartum_eligible", period.first_month
        ) & person("takes_up_chip_if_eligible", period)
        return takes_up & ~retained_chip
