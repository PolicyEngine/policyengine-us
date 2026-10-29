from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class ri_medicaid_state_funded_postpartum_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Rhode Island postpartum Medicaid outside the pregnancy group"
    documentation = (
        "Rhode Island's 12-month postpartum continuation for people whose "
        "pregnancy was not covered by Medicaid, or who lack Medicaid "
        "immigration status. It does not apply while a new pregnancy "
        "qualifies for Title XXI coverage that the person takes up."
    )
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://risos-apa-production-public.s3.amazonaws.com/EOHHS/REG_13314_20250728104245127.pdf#page=5",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0026.pdf#page=2",
    )

    def formula(person, period, parameters):
        continuation = person("ri_medicaid_postpartum_eligible", period.first_month)
        coverage = person("ri_pregnancy_coverage", period)
        pregnancy_group = (coverage == coverage.possible_values.MEDICAID) & person(
            "is_medicaid_immigration_status_eligible", period
        )
        state = person.household("state_code", period)
        chip_limit = parameters(period).gov.hhs.chip.pregnant.income_limit[state]
        title_xxi_pregnancy = (
            person("is_pregnant", period)
            & medicaid_income_eligible(person, period, parameters, chip_limit)
            & person("takes_up_chip_if_eligible", period)
        )
        return continuation & ~pregnancy_group & ~title_xxi_pregnancy
