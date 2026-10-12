from policyengine_us.model_api import *


class wi_ssp(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin State SSI Supplement"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WI
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    adds = ["wi_ssp_regular", "wi_ssi_e", "wi_cts"]
