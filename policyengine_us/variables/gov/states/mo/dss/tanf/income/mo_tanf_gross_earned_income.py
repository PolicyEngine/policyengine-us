from policyengine_us.model_api import *


class mo_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Only assistance unit members' income counts; excluded household
        # members (DSS Manual 0210.005.10) contribute neither needs nor
        # income.
        person = spm_unit.members
        member = person("mo_tanf_is_assistance_unit_member", period)
        earned = person("tanf_gross_earned_income", period)
        return spm_unit.sum(earned * member)
