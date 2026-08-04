from policyengine_us.model_api import *


class applicable_ssi(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Applicable SSI for program income tests"
    documentation = (
        "Deprecated: no program reads this variable anymore; programs count "
        "ssi directly, which partners can override by sending it as an "
        "input. Retained as an output for API partner compatibility until "
        "partners migrate (PolicyEngine/policyengine-us#9111). Uses "
        "calculated ssi by default; uses ssi_reported instead when "
        "use_reported_ssi is True."
    )

    def formula(person, period, parameters):
        use_reported = person("use_reported_ssi", period.this_year)
        return where(
            use_reported,
            person("ssi_reported", period),
            person("ssi", period),
        )
