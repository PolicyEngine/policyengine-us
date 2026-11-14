from policyengine_us.model_api import *


class nd_ccap_has_ineligible_kinship_caretaker(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    default_value = False
    label = "North Dakota CCAP family has an ineligible kinship caretaker with non-kinship children"
    documentation = (
        "Records whether an ineligible Kinship Care caretaker needs child care "
        "for non-kinship or non-TANF children in this family. "
        "North Dakota applies the co-payment under CCAP manual 400-28-90-20, "
        "except when some children qualify for TANF."
    )
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm"
