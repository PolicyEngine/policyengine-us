from policyengine_us.model_api import *


class md_non_refundable_eitc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD EITC non-refundable State tax credit"
    unit = USD
    documentation = "Non-refundable EITC credit reducing MD State income tax."
    definition_period = YEAR
    reference = "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false"
    defined_for = StateCode.MD

    adds = [
        "md_married_or_has_child_non_refundable_eitc",
        "md_unmarried_childless_non_refundable_eitc",
    ]
