from policyengine_us.model_api import *


class ny_ctc_post_2024(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC post-2024 rules"
    documentation = "New York's Empire State Child Credit under post-2024 rules (2025-2027)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY
    adds = ["ny_ctc_post_2024_base"]
    subtracts = ["ny_ctc_post_2024_phase_out"]
