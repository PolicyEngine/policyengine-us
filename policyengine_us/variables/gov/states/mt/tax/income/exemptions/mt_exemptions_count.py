from policyengine_us.model_api import *


class mt_exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of Montana exemptions"
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = [
        "head_spouse_count",
        "blind_head",
        "blind_spouse",
        "mt_dependent_exemption_count",
        "mt_aged_exemption_count",
    ]
