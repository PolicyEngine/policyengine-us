from policyengine_us.model_api import *


class is_complying_with_tanf_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Subject to and complying with TANF work requirements"
    documentation = (
        "Whether this person is subject to and complying with the work "
        "requirements of the Temporary Assistance for Needy Families "
        "(TANF) program under title IV of the Social Security Act. "
        "This is an input variable that the data layer may not yet "
        "populate; see PolicyEngine/populace#244."
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_iii"
