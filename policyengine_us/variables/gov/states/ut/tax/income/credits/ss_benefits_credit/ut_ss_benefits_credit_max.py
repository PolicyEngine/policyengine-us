from policyengine_us.model_api import *


class ut_ss_benefits_credit_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah Social Security Benefits Credit maximum amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://incometax.utah.gov/credits/ss-benefits"

    def formula(tax_unit, period, parameters):
        """
        This credit essentially makes social security tax-exempt for people earning
        under a threshold, and taxes it back after that.
        """
        taxable_social_security = add(
            tax_unit, period, ["taxable_social_security"]
        )  # Line 1
        total_income = tax_unit("ut_total_income", period)  # Line 2
        # Skip line 3 (muncipal bond interest)
        # Skip line 4 (subtract line 3 from line 2)

        tax_exempt_interest = add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )  # Line 5
        modified_agi = total_income + tax_exempt_interest  # Line 6
        p = parameters(period).gov.states.ut.tax.income
        taxed_ss = taxable_social_security * p.rate  # Line 7
        filing_status = tax_unit("filing_status", period)
        phase_out_income = max_(
            0,
            modified_agi
            - p.credits.ss_benefits.phase_out.threshold[filing_status],
        )  # Line 8
        phase_out_reduction = (
            phase_out_income * p.credits.ss_benefits.phase_out.rate
        )  # Line 9
        return max_(0, taxed_ss - phase_out_reduction)  # Line 10
