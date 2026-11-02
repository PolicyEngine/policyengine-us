from policyengine_us.model_api import *
from policyengine_us.tools.social_security.population import reported_pia_ratio_output


class social_security_dependents_pia_ratio_eligibility_year(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    unit = "year"
    label = "Social Security dependents pia-ratio eligibility year"
    documentation = "Underlying worker eligibility or computation year used by the population PIA-ratio calculation. Supplied record and worker links precede a labelled proxy; zero denotes an unavailable basis. Rebuilt independently in every scoring year."

    def formula(person, period, parameters):
        return reported_pia_ratio_output(
            person, period, parameters, "dependents", "eligibility_year"
        )
