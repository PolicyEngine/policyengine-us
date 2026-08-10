from policyengine_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    label = "SSI"
    documentation = "Supplemental Security Income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/42/1382"
    defined_for = "takes_up_ssi_if_eligible"
    adds = ["ssi_if_takes_up"]
