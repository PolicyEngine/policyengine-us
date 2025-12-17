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
        1. Get current income_tax
        2. Branch: Add employer SS to AGI, recalculate income_tax
        3. SS revenue = tax_with_ss - current_tax
        """
        sim = tax_unit.simulation

        # Check if reform is active
        p = parameters(period).gov.contrib.crfb.tax_employer_payroll_tax
        if not p.in_effect:
            return tax_unit.empty_array()

        # Get employer SS contribution (person-level, sum to tax unit)
        employer_ss = tax_unit.sum(
            tax_unit.members("employer_social_security_tax", period)
        )
        taxable_ss = p.percentage * employer_ss

        # Current tax (baseline)
        tax_baseline = tax_unit("income_tax", period)

        # === Branch: Tax WITH employer SS added to AGI ===
        branch = sim.get_branch("add_employer_ss", clone_system=True)

        # Clear cached calculations
        input_vars = set(branch.input_variables)
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        # Get current AGI and add employer SS
        current_agi = tax_unit("adjusted_gross_income", period)
        new_agi = current_agi + taxable_ss

        # Set the new AGI in the branch
        tax_unit_pop = branch.populations["tax_unit"]
        holder = tax_unit_pop.get_holder("adjusted_gross_income")
        holder.set_input(period, new_agi)

        tax_with_ss = branch.tax_unit("income_tax", period)
        del sim.branches["add_employer_ss"]

        # SS revenue = tax with SS - baseline tax
        return max_(tax_with_ss - tax_baseline, 0)
