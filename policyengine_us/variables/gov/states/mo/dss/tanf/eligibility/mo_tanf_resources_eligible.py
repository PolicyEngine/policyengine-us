from policyengine_us.model_api import *


class mo_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Missouri TANF resource eligibility"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0205-005-00/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # 13 CSR 40-2.310(3) raises the limit to $5,000 for participants
        # in an Individual Employment Plan (DSS Manual 0205.005.00: "$5,000
        # for participant families who have entered into a self sufficiency
        # pact"); IEP participation is not observable, so the $1,000 limit
        # applies to all units.
        p = parameters(period).gov.states.mo.dss.tanf.resource_limit
        resources = spm_unit("mo_tanf_countable_resources", period)
        return resources <= p.amount
