from policyengine_us.model_api import *


class mo_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF resource eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.tanf.resource_limit

        # Get MO TANF countable resources
        countable_resources = spm_unit("mo_tanf_countable_resources", period)

        # Check if household has signed Individual Employment Plan
        has_iep = spm_unit("mo_tanf_has_individual_employment_plan", period)

        # Select appropriate resource limit
        resource_limit = where(has_iep, p.with_iep, p.initial_application)

        return countable_resources <= resource_limit
