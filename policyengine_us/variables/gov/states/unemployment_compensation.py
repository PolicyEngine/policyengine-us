from policyengine_us.model_api import *


class unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "unemployment compensation"
    unit = USD
    documentation = (
        "Income from unemployment compensation programs. "
        "Auto-populates modeled state UI where available and may otherwise be "
        "provided as an input."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.unemployment_compensation"

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        return where(
            state_code == StateCode.NJ,
            person("nj_unemployment_insurance", period),
            0,
        )
