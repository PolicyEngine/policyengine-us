from policyengine_us.model_api import *


class va_child_dependent_care_deduction_cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal CDCC-relevant care expense limit for Virginia tax purposes"
    unit = USD
    definition_period = YEAR
    reference = (
        # Revised 2021 Form 760PY code 101 instructions and resident deduction.
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760py-instructions.pdf#page=28",
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-322.03/",
        "https://www.tax.virginia.gov/sites/default/files/inline-files/tb-22-1-irc-conformity-advanced.pdf#page=1",
        "https://lis.virginia.gov/cgi-bin/legp604.exe?221+ful+CHAP0003",
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        # 2022 Va. Acts ch. 3 (HB 971) advanced Virginia's IRC conformity to
        # December 31, 2021 with effect for 2021 returns, so 2021 uses the
        # ARPA $8,000 / $16,000 limit and the $10,500 IRC section 129 cap.
        # The revised 2021 Form 760PY code 101 instructions specify $8,000
        # for one dependent and $16,000 for two or more. Tax Bulletin 22-1
        # confirms the same conformity change for Virginia individual taxes.
        p = parameters(period).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit("capped_count_cdcc_eligible", period)
        dollar_limit = p.max * capped_count_cdcc_eligible
        # Va. Code § 58.1-322.03(3) deducts "the amount of employment-related
        # expenses upon which the federal credit is based under § 21," and the
        # Form 760 code 101 instruction points to the Form 2441 amount that is
        # multiplied by the decimal (line 31) — already reduced by the IRC § 129
        # employer-provided dependent care benefits under § 21(c). Mirror that
        # reduction so the deduction base matches the federal credit's base.
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        return max_(dollar_limit - exclusion, 0)
