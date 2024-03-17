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
        # States where we model childcare subsidies.
        STATES_WITH_CHILD_CARE_SUBSIDIES = ["CA", "CO"]
        subsidy_variables = [
            i.lower() + "_child_care_subsidies"
            for i in STATES_WITH_CHILD_CARE_SUBSIDIES
        ]
        subsidies = add(spm_unit, period, subsidy_variables)
        return max_(pre_subsidy_childcare_expenses - subsidies, 0)
