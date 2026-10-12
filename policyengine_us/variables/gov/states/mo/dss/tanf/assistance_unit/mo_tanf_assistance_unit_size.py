from policyengine_us.model_api import *


class mo_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Missouri TANF assistance unit size"
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    adds = ["mo_tanf_is_assistance_unit_member"]
