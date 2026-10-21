from policyengine_us.model_api import *


class va_ccsp_enrolled(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Whether the family is currently enrolled in Virginia Child Care Subsidy Program"
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section40/",
        "https://ris.dls.virginia.gov/uploads/22VAC40/dibr/VDOE%20Child%20Care%20Program%20Guidance%20Manual%205.3.2023-20240822104447.pdf#page=90",
    )
