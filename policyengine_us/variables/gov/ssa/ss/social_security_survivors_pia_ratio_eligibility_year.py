from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_survivors_pia_ratio_eligibility_year(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    unit = "year"
    label = "Social Security survivors pia-ratio eligibility year"
    documentation = "Underlying worker eligibility or computation year used by the population PIA-ratio calculation. Supplied record and worker links precede a labelled proxy; zero denotes an unavailable basis. Rebuilt independently in every scoring year."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "survivors", "eligibility_year"
        )
