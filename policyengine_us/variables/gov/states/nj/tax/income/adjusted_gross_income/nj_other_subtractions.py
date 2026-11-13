from policyengine_us.model_api import *


class nj_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    documentation = (
        "Amounts PolicyEngine includes in New Jersey gross income that are exempt from "
        "New Jersey tax (Form NJ-1040 has no subtractions line), entered as a positive amount. "
        "Do not include U.S. government obligation interest, which PolicyEngine excludes separately."
    )
    reference = "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf"
