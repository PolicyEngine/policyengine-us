from policyengine_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        pre_subsidy_childcare_expenses = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        subsidies = spm_unit("child_care_subsidies", period)
        # Charges a subsidy program bars the provider from collecting never
        # reach the family.
        absorbed = spm_unit("child_care_charges_providers_absorb", period)
        return max_(pre_subsidy_childcare_expenses - subsidies - absorbed, 0)
