from policyengine_us.model_api import *


class vt_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont TANF (Reach Up)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://legislature.vermont.gov/statutes/fullchapter/33/011",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = "vt_tanf_eligible"

    def formula(spm_unit, period, parameters):
        # Per Rule 2239 and 2242: Benefit = payment standard - countable income
        # Minimum benefit is $10; amounts below this are not paid
        p = parameters(period).gov.states.vt.dcf.tanf.benefit
        payment_standard = spm_unit("vt_tanf_payment_standard", period)
        countable_income = spm_unit("vt_tanf_countable_income", period)
        gross_benefit = max_(payment_standard - countable_income, 0)
        # Per Rule 2242: No payment if benefit < minimum
        return where(gross_benefit >= p.minimum, gross_benefit, 0)
