from policyengine_us.model_api import *


class mo_tanf_has_individual_employment_plan(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF household has signed Individual Employment Plan"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO
