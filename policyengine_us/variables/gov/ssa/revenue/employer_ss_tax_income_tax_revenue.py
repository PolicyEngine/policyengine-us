from policyengine_us.model_api import *


class employer_ss_tax_income_tax_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax revenue from taxing employer SS contributions"
    documentation = (
        "Marginal income tax revenue attributable to including employer "
        "Social Security contributions in taxable income. This revenue "
        "is credited to the OASDI trust funds."
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        """
        Calculate OASDI trust fund revenue from employer SS taxation.

        Method:
        1. Get current income_tax (with BOTH SS + Medicare in AGI from reform)
        2. Branch: Neutralize employer_social_security_tax, recalculate income_tax
        3. SS revenue = current_tax - tax_without_ss

        This isolates the marginal tax contribution from employer SS by
        neutralizing the source variable, letting the reform formula
        naturally exclude SS when calculating gross income.
        """
        sim = tax_unit.simulation

        # Check if reform is active
        p = parameters(period).gov.contrib.crfb.tax_employer_payroll_tax
        if not p.in_effect:
            return tax_unit.empty_array()

        # Current tax (with reform - both SS and Medicare in AGI)
        tax_full = tax_unit("income_tax", period)

        # === Branch: Tax WITHOUT employer SS (neutralize source) ===
        branch = sim.get_branch("without_employer_ss", clone_system=True)

        # Neutralize the source variable - reform formula will pick up 0 for SS
        branch.tax_benefit_system.neutralize_variable(
            "employer_social_security_tax"
        )

        # Clear cached calculations
        input_vars = set(branch.input_variables)
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        tax_without_ss = branch.tax_unit("income_tax", period)
        del sim.branches["without_employer_ss"]

        # SS revenue = tax with full reform - tax without SS
        return max_(tax_full - tax_without_ss, 0)
