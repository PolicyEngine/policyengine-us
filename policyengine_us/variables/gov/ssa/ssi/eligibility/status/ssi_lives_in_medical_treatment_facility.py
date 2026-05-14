from policyengine_us.model_api import *


class ssi_lives_in_medical_treatment_facility(Variable):
    value_type = bool
    entity = Person
    label = "Lives in a medical treatment facility for SSI purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0500520001",
    )
