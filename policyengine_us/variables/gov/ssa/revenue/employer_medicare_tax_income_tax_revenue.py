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
        1. Get current income_tax
        2. Branch: Add employer Medicare to AGI, recalculate income_tax
        3. Medicare revenue = tax_with_medicare - current_tax
        """
        sim = tax_unit.simulation

        # Check if reform is active
        p = parameters(period).gov.contrib.crfb.tax_employer_payroll_tax
        if not p.in_effect:
            return tax_unit.empty_array()

        # Get employer Medicare contribution (person-level, sum to tax unit)
        employer_medicare = tax_unit.sum(
            tax_unit.members("employer_medicare_tax", period)
        )
        taxable_medicare = p.percentage * employer_medicare

        # Current tax (baseline)
        tax_baseline = tax_unit("income_tax", period)

        # === Branch: Tax WITH employer Medicare added to AGI ===
        branch = sim.get_branch("add_employer_medicare", clone_system=True)

        # Clear cached calculations
        input_vars = set(branch.input_variables)
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        # Get current AGI and add employer Medicare
        current_agi = tax_unit("adjusted_gross_income", period)
        new_agi = current_agi + taxable_medicare

        # Set the new AGI in the branch
        tax_unit_pop = branch.populations["tax_unit"]
        holder = tax_unit_pop.get_holder("adjusted_gross_income")
        holder.set_input(period, new_agi)

        tax_with_medicare = branch.tax_unit("income_tax", period)
        del sim.branches["add_employer_medicare"]

        # Medicare revenue = tax with Medicare - baseline tax
        return max_(tax_with_medicare - tax_baseline, 0)
