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

        # Use SPMUnit assets as proxy for countable resources
        # In full implementation, would need specific MO resource definitions
        spm_assets = add(spm_unit, period, ["spm_unit_net_income_reported"])

        # Use initial application limit (simplified)
        # Full implementation would track whether IEP is signed
        resource_limit = p.initial_application

        return spm_assets <= resource_limit
