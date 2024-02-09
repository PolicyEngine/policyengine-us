from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_joint(Variable):
    value_type = float
    entity = Person
    label = (
        "Delaware aged or disabled exclusion when married couple files jointly"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1"
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # Allocate the exemptions to the head
        exclusions = add(
            person.tax_unit,
            period,
            ["de_elderly_or_disabled_income_exclusion_indv"],
        )
        head = person("is_tax_unit_head", period)
        return exclusions * head
