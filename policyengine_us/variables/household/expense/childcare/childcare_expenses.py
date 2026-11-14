from policyengine_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        # On its sample invoices in a January 13, 2026 memo on prekindergarten
        # and CCFAP tuition (PDF pages 1 and 6), Vermont's Child Development
        # Division takes the state's payment off tuition.
        pre_subsidy_childcare_expenses = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        subsidies = spm_unit("child_care_subsidies", period)
        return max_(pre_subsidy_childcare_expenses - subsidies, 0)
