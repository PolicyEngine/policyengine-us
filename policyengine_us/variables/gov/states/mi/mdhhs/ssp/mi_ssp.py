from policyengine_us.model_api import *


class mi_ssp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Michigan State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-400-10",
    )

    adds = ["mi_ssp_person"]
