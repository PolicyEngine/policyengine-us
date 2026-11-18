from policyengine_us.model_api import *


class ri_chip_postpartum_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Rhode Island postpartum CHIP continuation"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = (
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0025.pdf#page=4",
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
    )

    def formula(person, period, parameters):
        coverage = person("ri_pregnancy_coverage", period.this_year)
        return person("ri_medicaid_postpartum_eligible", period) & (
            coverage == coverage.possible_values.CHIP
        )
