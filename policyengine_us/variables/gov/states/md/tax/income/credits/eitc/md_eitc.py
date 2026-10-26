from policyengine_us.model_api import *


class md_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total EITC"
    unit = USD
    documentation = "Refundable and non-refundable Maryland EITC"
    definition_period = YEAR
    reference = "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false"
    defined_for = StateCode.MD

    adds = ["md_non_refundable_eitc", "md_refundable_eitc"]
