from policyengine_us.model_api import *


class tob_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI trust fund revenue from SS benefit taxation"
    documentation = (
        "Increase in chapter 1 income tax liability after nonrefundable credits and "
        "before refundable credits credited to OASDI trust funds per "
        "42 U.S.C. 401 note. Excludes chapter 2A net investment income tax "
        "under section 1411. "
        "Per Section 121(e) of PL 98-21, OASDI receives the 'increase in tax "
        "liabilities attributable to' section 86 LESS the 1993 amendments. "
        "Calculated using branching to isolate the signed marginal tax "
        "impact. Negative unit differences are retained when aggregating "
        "tax liabilities. Actual inclusion caps the old-law inclusion. When "
        "a reform cuts inclusion below the pre-1993 amount, the 1993 "
        "amendments add nothing, and OASDI takes the whole increase."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/401",
        "https://www.law.cornell.edu/uscode/text/26/1411",
        "https://www.ssa.gov/OP_Home/comp2/F098-021.html",
    )

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue using double-branching.

        OASDI gets the tax attributable to the pre-1993 section 86 inclusion,
        including its provisional-income limit, under current income tax rules.
        Actual inclusion caps the old-law inclusion. At current law the cap
        changes nothing, because both laws share the first tier. When a reform
        cuts inclusion below the pre-1993 amount, the 1993 amendments add
        nothing, so OASDI takes the whole increase and HI none.

        Method:
        1. Calculate chapter 1 tax with NO taxable SS
        2. Calculate chapter 1 tax with the lesser of the pre-1993 section 86
           includible amount and actual inclusion
        3. Signed OASDI revenue = (2) - (1), without a per-unit floor
        """
        # Each state is cached on the parent after its branch is released.
        # The capped old-law state reads actual inclusion in this simulation.
        tax_old_law_ss = tax_unit("income_tax_with_pre_1993_social_security", period)
        tax_no_ss = tax_unit("income_tax_without_social_security", period)

        return tax_old_law_ss - tax_no_ss
