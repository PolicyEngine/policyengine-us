from policyengine_us.model_api import *


class medicaid_federal_cost(Variable):
    value_type = float
    entity = Person
    label = "Medicaid federal cost"
    documentation = (
        "Portion of Medicaid expenditures borne by the federal government, "
        "equal to total Medicaid cost multiplied by the applicable FMAP."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396b"
    defined_for = "medicaid_enrolled"

    def formula(person, period, parameters):
        return person("medicaid_cost", period) * person(
            "medicaid_federal_share", period
        )
