from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_dependents_pia_ratio_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = "/1"
    label = "Social Security dependents PIA ratio factor"
    documentation = (
        "Eligibility-year reformed-to-baseline PIA ratio for the reported source. "
        "Calculated sources bypass this factor. Unsupported or unmodeled records "
        "remain at one and expose separate diagnostic indicators."
    )

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "dependents", "factor"
        )
