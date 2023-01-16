from policyengine_us.model_api import *


class ctc_arpa_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Additional CTC from ARPA"
    unit = USD
    definition_period = YEAR
    # Defined on Line 5 worksheet of 2021 Instructions for Schedule 8812.
    reference = "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4"
    adds = ["ctc_arpa_max_addition"]
    subtracts = ["ctc_arpa_phase_out"]
