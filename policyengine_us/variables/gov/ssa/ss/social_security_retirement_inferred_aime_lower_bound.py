from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_retirement_inferred_aime_lower_bound(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = (
        "Social Security retirement inferred eligibility-year monthly aime lower bound"
    )
    documentation = "Inclusive lower endpoint of the conditional baseline-inversion interval in monthly AIME dollars. This is a PIA-rounding interval, not a confidence interval for survey measurement error."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "retirement", "aime_lower"
        )
