from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_retirement_inferred_aime_upper_bound(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = (
        "Social Security retirement inferred eligibility-year monthly aime upper bound"
    )
    documentation = "Exclusive upper endpoint of the conditional baseline-inversion interval in monthly AIME dollars. Any configured annual rounding bound is propagated backward; additional survey measurement error is not quantified."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "retirement", "aime_upper"
        )
