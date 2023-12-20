from policyengine_us.model_api import *


class mt_exemptions_count_joint(Variable):
    value_type = int
    entity = TaxUnit
    label = "Montana exemptions when married couple files jointly"
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = [
        "head_spouse_count",
        "blind_head",
        "blind_spouse",
        "mt_dependent_exemption_joint",
        "mt_aged_exemption_joint",
    ]
