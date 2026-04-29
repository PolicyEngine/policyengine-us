from policyengine_us.model_api import *


class va_ccsp_income_test_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income test waived for Virginia Child Care Subsidy Program"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/admincode/title8/agency20/chapter790/section30/",
        "https://www.childcare.virginia.gov/home/showpublisheddocument/66667/638981099706730000#page=29",
    )

    def formula(spm_unit, period, parameters):
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        has_medicaid = spm_unit.any(person("receives_medicaid", period.this_year))
        has_wic = spm_unit.any(person("receives_wic", period))
        return tanf_enrolled | has_medicaid | has_wic
