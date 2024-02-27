from policyengine_us.model_api import *


class tax_unit_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # distribute the SPM unit's childcare expenses evenly across
        # children in SPM unit's Tax units
        spm_unit = tax_unit.spm_unit
        spm_unit_childcare = spm_unit("childcare_expenses", period)
        spm_unit_count_children = add(spm_unit, period, ["is_child"])
        tax_unit_count_children = add(tax_unit, period, ["is_child"])
        # avoid array divide-by-zero warning by not using where() function
        # see the following GitHub issue for more details:
        # https://github.com/PolicyEngine/policyengine-us/issues/2494
        child_ratio = np.zeros_like(spm_unit_count_children)
        mask = spm_unit_count_children > 0
        child_ratio[mask] = (
            tax_unit_count_children[mask] / spm_unit_count_children[mask]
        )
        return spm_unit_childcare * child_ratio
