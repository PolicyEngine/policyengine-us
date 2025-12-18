from policyengine_us.model_api import *


class employer_medicare_tax_income_tax_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax revenue from taxing employer Medicare contributions"
    documentation = (
        "Marginal income tax revenue attributable to including employer "
        "Medicare contributions in taxable income. This revenue "
        "is credited to the Medicare HI trust fund."
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        """
        Calculate Medicare HI trust fund revenue from employer Medicare taxation.

        Method:
        1. Get current income_tax (with BOTH SS + Medicare in AGI from reform)
        2. Branch: Neutralize employer_medicare_tax, recalculate income_tax
        3. Medicare revenue = current_tax - tax_without_medicare

        This isolates the marginal tax contribution from employer Medicare by
        neutralizing the source variable, letting the reform formula
        naturally exclude Medicare when calculating gross income.
        """
        sim = tax_unit.simulation

        # Check if reform is active
        p = parameters(period).gov.contrib.crfb.tax_employer_payroll_tax
        if not p.in_effect:
            return tax_unit.empty_array()

        # Current tax (with reform - both SS and Medicare in AGI)
        tax_full = tax_unit("income_tax", period)

        # === Branch: Tax WITHOUT employer Medicare (neutralize source) ===
        branch = sim.get_branch("without_employer_medicare", clone_system=True)

        # Neutralize the source variable - reform formula will pick up 0 for Medicare
        branch.tax_benefit_system.neutralize_variable("employer_medicare_tax")

        # Clear cached calculations
        input_vars = set(branch.input_variables)
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        tax_without_medicare = branch.tax_unit("income_tax", period)
        del sim.branches["without_employer_medicare"]

        # Medicare revenue = tax with full reform - tax without Medicare
        return max_(tax_full - tax_without_medicare, 0)
