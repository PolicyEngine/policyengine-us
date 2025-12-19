from policyengine_us.model_api import *


class tob_revenue_medicare_hi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medicare HI trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue credited to Medicare HI trust fund per 42 U.S.C. 401 note. "
        "Per Section 121(e) as amended by OBRA 1993, HI receives the 'increase "
        "in tax liabilities attributable to' the 1993 amendments. "
        "Calculated using branching to isolate marginal tax impact."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/401"

    def formula(tax_unit, period, parameters):
        """
        Calculate Medicare HI trust fund revenue using double-branching.

        HI gets the marginal tax impact of adding the portion of taxable SS
        above 50% of gross (the 1993 amendment increment).

        Method:
        1. Calculate tax with 50% of gross SS taxable (capped)
        2. Calculate tax with FULL taxable SS (current law)
        3. HI revenue = (2) - (1)
        """
        sim = tax_unit.simulation
        p = parameters(period).gov.ssa.revenue

        # Get current values
        gross_ss = tax_unit("tax_unit_social_security", period)
        taxable_ss = tax_unit("tax_unit_taxable_social_security", period)

        # Calculate the OASDI share cap
        oasdi_share = p.oasdi_share_of_gross_ss * gross_ss
        capped_taxable_ss = min_(taxable_ss, oasdi_share)

        # === Current tax (with full taxable SS) ===
        tax_full_ss = tax_unit("income_tax", period)

        # === Branch: Tax with CAPPED taxable SS (50% of gross) ===
        branch_capped = sim.get_branch("hi_capped", clone_system=True)

        # Clear only non-input cached calculations before setting new value
        input_vars = set(branch_capped.input_variables)
        for var_name in list(
            branch_capped.tax_benefit_system.variables.keys()
        ):
            if var_name not in input_vars:
                try:
                    branch_capped.delete_arrays(var_name)
                except:
                    pass

        # Set taxable SS to the capped amount using holder
        tax_unit_pop = branch_capped.populations["tax_unit"]
        holder = tax_unit_pop.get_holder("tax_unit_taxable_social_security")
        holder.set_input(period, capped_taxable_ss)

        tax_capped_ss = branch_capped.tax_unit("income_tax", period)
        del sim.branches["hi_capped"]

        # HI revenue = tax with full SS - tax with 50% cap
        return max_(tax_full_ss - tax_capped_ss, 0)
