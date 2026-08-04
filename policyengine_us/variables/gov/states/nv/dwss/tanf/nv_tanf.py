from policyengine_us.model_api import *


class nv_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = "https://dwss.nv.gov/siteassets/dwss.nv.gov/ep-manual-section-a/chapter-a-600-budgeting-ada-8.2025.pdf#page=38"
    defined_for = "nv_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.tanf
        payment_standard = spm_unit("nv_tanf_payment_standard", period)
        countable_income = spm_unit("nv_tanf_countable_income", period)
        # Benefit is payment standard minus countable income
        benefit = max_(payment_standard - countable_income, 0)
        # Cap benefit at payment standard to prevent negative income
        # from inflating benefits above the maximum.
        benefit = min_(benefit, payment_standard)
        # E&P Manual A-660.12: "A benefit is always a whole dollar amount.
        # Round all amounts down to the nearest dollar."
        benefit = np.floor(benefit)
        # A-660.12: "The minimum benefit amount is $10." Regular monthly
        # benefits below $10 are not issued (only supplemental payments and
        # post-overpayment-recoupment payments, which PolicyEngine does not
        # model, may fall below $10).
        return where(benefit >= p.minimum_payment, benefit, 0)
