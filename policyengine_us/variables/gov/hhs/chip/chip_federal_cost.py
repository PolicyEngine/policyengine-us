from policyengine_us.model_api import *


class chip_federal_cost(Variable):
    value_type = float
    entity = Person
    label = "CHIP federal cost"
    documentation = (
        "Portion of CHIP expenditures borne by the federal government, "
        "equal to total CHIP cost multiplied by the enhanced FMAP."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1397ee#b"
    defined_for = "chip_enrolled"

    def formula(person, period, parameters):
        return person("chip", period) * person("chip_federal_share", period)
