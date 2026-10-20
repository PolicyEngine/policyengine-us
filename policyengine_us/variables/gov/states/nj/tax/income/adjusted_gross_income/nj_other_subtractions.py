from policyengine_us.model_api import *


class nj_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    documentation = (
        "New Jersey other subtractions from federal adjusted gross income reported on "
        "Form NJ-1040, entered as a positive amount. Do not include U.S. government "
        "obligation interest, which PolicyEngine computes separately."
    )
    reference = "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf"
