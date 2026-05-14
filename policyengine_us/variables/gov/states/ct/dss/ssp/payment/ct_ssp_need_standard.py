from policyengine_us.model_api import *


class ct_ssp_need_standard(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP need standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#4520.10",
    )

    adds = [
        "ct_ssp_shelter_allowance",
        "ct_ssp_personal_needs_allowance",
        "ct_ssp_special_needs",
    ]
