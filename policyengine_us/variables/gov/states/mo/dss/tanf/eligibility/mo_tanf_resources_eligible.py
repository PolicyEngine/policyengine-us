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
        resources = spm_unit("spm_unit_cash_assets", period.this_year)
        return resources <= p.amount
