from policyengine_us.model_api import *


class tob_revenue_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Total trust fund revenue from SS benefit taxation"
    documentation = (
        "Tax revenue from taxation of Social Security benefits using "
        "branching methodology per 42 U.S.C. 401 note."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/401"

    def formula(tax_unit, period, parameters):
        """
        Calculate total trust fund revenue using branching + neutralization.

        This isolates the tax impact of including taxable SS in AGI by
        comparing tax with and without taxable SS.
        """
        sim = tax_unit.simulation

        # Calculate income tax WITH taxable SS
        income_tax_with_ss = tax_unit("income_tax", period)

        # Create branch and neutralize taxable SS
        branch = sim.get_branch("tob_calc", clone_system=True)
        branch.tax_benefit_system.neutralize_variable(
            "tax_unit_taxable_social_security"
        )

        # Delete non-input cached variables to force recalculation
        input_vars = set(branch.input_variables)
        for var_name in list(branch.tax_benefit_system.variables.keys()):
            if var_name not in input_vars:
                try:
                    branch.delete_arrays(var_name)
                except:
                    pass

        # Recalculate income tax without taxable SS
        income_tax_without_ss = branch.tax_unit("income_tax", period)

        # Clean up branch
        del sim.branches["tob_calc"]

        return income_tax_with_ss - income_tax_without_ss
