from policyengine_us.model_api import *


class mo_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-010-15/",
    )
    defined_for = "mo_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_benefit = spm_unit("mo_tanf_maximum_benefit", period)
        countable_income = spm_unit("mo_tanf_countable_income", period)
        benefit = max_(maximum_benefit - countable_income, 0)
        p = parameters(period).gov.states.mo.dss.tanf
        return where(benefit >= p.minimum_payment, benefit, 0)
