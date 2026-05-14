from policyengine_us.model_api import *


class in_resides_in_unlicensed_residential_facility(Variable):
    value_type = bool
    entity = Person
    label = "Resides in an Indiana unlicensed residential care facility"
    definition_period = YEAR
    defined_for = StateCode.IN
    default_value = False
    reference = (
        "https://www.law.cornell.edu/regulations/indiana/455-IAC-1-3-3",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/in.html",
    )
