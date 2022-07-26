from openfisca_us.model_api import *


class in_other_local_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN other non-refundable credits that offset county tax"
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3.1-19"
    )
