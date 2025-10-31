from policyengine_us.model_api import *


class tob_revenue_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Total trust fund revenue from SS benefit taxation"
    documentation = "Tax revenue from taxation of Social Security benefits using branching methodology"
    unit = USD

    def formula(tax_unit, period, parameters):
        """
        Calculate trust fund revenue using branching + neutralization.

        This is the CORRECT way to isolate TOB revenue, superior to the
        average effective tax rate approximation.
        """
        sim = tax_unit.simulation

        # Calculate income tax WITH taxable SS
        income_tax_with = tax_unit("income_tax", period)

        # Create branch and neutralize taxable SS
        branch = sim.get_branch("tob_calc", clone_system=True)
        branch.tax_benefit_system.neutralize_variable(
            "tax_unit_taxable_social_security"
        )

        # Delete all calculated variables to force recalculation
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in branch.input_variables:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        # Recalculate income tax without taxable SS
        income_tax_without = branch.tax_unit("income_tax", period)

        # Clean up branch
        del sim.branches["tob_calc"]

        return income_tax_with - income_tax_without
