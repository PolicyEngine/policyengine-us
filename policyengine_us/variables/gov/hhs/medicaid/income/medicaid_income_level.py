from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_income_level(Variable):
    value_type = float
    entity = Person
    label = "Medicaid/CHIP-related income level"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603",
        "https://www.medicaid.gov/state-resource-center/mac-learning-collaboratives/downloads/household-composition-and-income-training.pdf",
    )

    def formula(person, period, parameters):
        income = person("medicaid_household_income", period)
        size = person("medicaid_household_size", period)
        state_group = person.household("state_group_str", period)
        return income / fpg(size, state_group, period, parameters)
