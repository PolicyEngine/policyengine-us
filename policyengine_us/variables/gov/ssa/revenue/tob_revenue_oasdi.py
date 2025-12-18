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
        "Calculated using branching to isolate marginal tax impact."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/401"

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue using double-branching.

        OASDI gets the marginal tax impact of adding the first 50% of
        gross SS benefits to taxable income.

        Method:
        1. Calculate tax with NO taxable SS
        2. Calculate tax with 50% of gross SS taxable (capped)
        3. OASDI revenue = (2) - (1)
        """
        sim = tax_unit.simulation
        p = parameters(period).gov.ssa.revenue

        # Get current values
        gross_ss = tax_unit("tax_unit_social_security", period)
        taxable_ss = tax_unit("tax_unit_taxable_social_security", period)

        # Calculate the OASDI share cap - the original 1983 tier
        oasdi_share = p.oasdi_share_of_gross_ss * gross_ss
        capped_taxable_ss = min_(taxable_ss, oasdi_share)

        # === Branch 1: Tax with NO taxable SS ===
        branch_no_ss = sim.get_branch("oasdi_no_ss", clone_system=True)
        branch_no_ss.tax_benefit_system.neutralize_variable(
            "tax_unit_taxable_social_security"
        )

        # Clear only non-input cached calculations
        input_vars = set(branch_no_ss.input_variables)
        for var_name in list(branch_no_ss.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch_no_ss.delete_arrays(var_name)
                except:
                    pass

        tax_no_ss = branch_no_ss.tax_unit("income_tax", period)
        del sim.branches["oasdi_no_ss"]

        # === Branch 2: Tax with CAPPED taxable SS (50% of gross) ===
        branch_capped = sim.get_branch("oasdi_capped", clone_system=True)

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
        del sim.branches["oasdi_capped"]

        # OASDI revenue = tax with 50% cap - tax with no SS
        return max_(tax_capped_ss - tax_no_ss, 0)
