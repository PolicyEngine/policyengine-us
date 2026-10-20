from policyengine_us.model_api import *


class nj_other_additions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    documentation = (
        "New Jersey other additions to gross income reported on Form NJ-1040, "
        "line 26 (Other), entered as a positive amount."
    )
    reference = "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf"
