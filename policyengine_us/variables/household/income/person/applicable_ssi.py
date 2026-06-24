from policyengine_us.model_api import *


class applicable_ssi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Applicable SSI for program income tests"
    documentation = (
        "SSI amount counted in program income tests. Uses calculated ssi "
        "by default; uses ssi_reported instead when use_reported_ssi is True."
    )

    def formula(person, period, parameters):
        use_reported = person("use_reported_ssi", period)
        return where(
            use_reported,
            person("ssi_reported", period),
            person("ssi", period),
        )
