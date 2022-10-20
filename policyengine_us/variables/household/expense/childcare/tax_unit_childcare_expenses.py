from policyengine_us.model_api import *
import warnings

warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


class tax_unit_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Distribute the childcare expenses evenly across the SPM unit's members.
        spm_unit = tax_unit.spm_unit
        spm_unit_childcare = spm_unit("childcare_expenses", period)
        spm_unit_count_children = add(spm_unit, period, ["is_child"])
        tax_unit_count_children = add(tax_unit, period, ["is_child"])
        child_ratio = where(
            spm_unit_count_children > 0,
            tax_unit_count_children / spm_unit_count_children,
            0,
        )
        return spm_unit_childcare * child_ratio
