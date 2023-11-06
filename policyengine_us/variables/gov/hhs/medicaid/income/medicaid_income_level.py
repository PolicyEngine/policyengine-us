from policyengine_us.model_api import *


class medicaid_income_level(Variable):
    value_type = float
    entity = Person
    label = "Medicaid/CHIP-related income level"
    unit = "/1"
    documentation = (
        "Modified AGI as a fraction of current-year federal poverty line."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        return person.tax_unit("tax_unit_medicaid_income_level", period)
