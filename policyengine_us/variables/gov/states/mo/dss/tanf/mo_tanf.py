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
        p = parameters(period).gov.states.mo.dss.tanf
        maximum_benefit = spm_unit("mo_tanf_maximum_benefit", period)
        countable_income = spm_unit("mo_tanf_countable_income", period)

        # Benefit = Maximum Benefit - Countable Income
        calculated_benefit = maximum_benefit - countable_income

        # Round down to nearest dollar
        benefit_rounded = np.floor(calculated_benefit)

        # No payment if benefit < $10
        minimum_payment = p.minimum_payment.threshold
        benefit = where(benefit_rounded >= minimum_payment, benefit_rounded, 0)

        return max_(benefit, 0)
