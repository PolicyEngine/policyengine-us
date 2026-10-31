from policyengine_us.model_api import *


class tob_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue credited to OASDI trust funds per 42 U.S.C. 401 note. "
        "Per Section 121(e) of PL 98-21, OASDI receives the 'increase in tax "
        "liabilities attributable to' section 86 LESS the 1993 amendments. "
        "Calculated using branching to isolate the signed marginal tax "
        "impact. Negative unit differences are retained when aggregating "
        "tax liabilities."
    )
    unit = USD
    reference = "https://www.ssa.gov/OP_Home/comp2/F098-021.html"

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue using double-branching.

        OASDI gets the tax attributable to the pre-1993 section 86 inclusion,
        including its provisional-income limit, under current income tax rules.

        Method:
        1. Calculate tax with NO taxable SS
        2. Calculate tax with the pre-1993 section 86 includible amount
        3. Signed OASDI revenue = (2) - (1), without a per-unit floor
        """
        # Each state is cached on the parent after its branch is released.
        tax_no_ss = tax_unit("income_tax_without_social_security", period)
        tax_old_law_ss = tax_unit("income_tax_with_pre_1993_social_security", period)

        return tax_old_law_ss - tax_no_ss
