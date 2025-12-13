from policyengine_us.model_api import *


class mo_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Missouri Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        demographic = person("is_person_demographic_tanf_eligible", period)
        has_eligible_member = spm_unit.any(demographic)
        income_eligible = spm_unit("mo_tanf_income_eligible", period)
        resources_eligible = spm_unit("mo_tanf_resources_eligible", period)
        return has_eligible_member & income_eligible & resources_eligible
