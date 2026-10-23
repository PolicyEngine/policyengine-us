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
        sim = tax_unit.simulation
        old_law_taxable_ss = tax_unit(
            "tax_unit_taxable_social_security_pre_1993", period
        )

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

        # === Branch 2: Tax with the pre-1993 includible amount ===
        branch_old_law = sim.get_branch("oasdi_old_law", clone_system=True)

        # Clear only non-input cached calculations before setting new value
        input_vars = set(branch_old_law.input_variables)
        for var_name in list(branch_old_law.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch_old_law.delete_arrays(var_name)
                except:
                    pass

        # Override taxable SS after clearing computed arrays, preserving inputs.
        tax_unit_pop = branch_old_law.populations["tax_unit"]
        holder = tax_unit_pop.get_holder("tax_unit_taxable_social_security")
        holder.set_input(period, old_law_taxable_ss)

        tax_old_law_ss = branch_old_law.tax_unit("income_tax", period)
        del sim.branches["oasdi_old_law"]

        return tax_old_law_ss - tax_no_ss
