from policyengine_us.model_api import *


class mo_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Missouri Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.040",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-325",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # RSMo 208.040 grants Temporary Assistance only on behalf of a
        # dependent child; pregnancy alone does not qualify a household
        # (13 CSR 40-2.325 has no unborn-child provision).
        dependent_child = person("mo_tanf_dependent_child", period)
        member = person("mo_tanf_is_assistance_unit_member", period)
        has_eligible_child = spm_unit.any(dependent_child & member)
        income_eligible = spm_unit("mo_tanf_income_eligible", period)
        resources_eligible = spm_unit("mo_tanf_resources_eligible", period)
        return has_eligible_child & income_eligible & resources_eligible
