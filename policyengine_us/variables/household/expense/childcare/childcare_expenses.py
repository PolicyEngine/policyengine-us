from policyengine_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD
    # Vermont's sample invoices take the state's payment off tuition. PDF pages 1 and 6.
    reference = "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/CDD-Memo-UPK-and-CCFAP-family-tuition%20(1).pdf#page=6"

    def formula(spm_unit, period, parameters):
        pre_subsidy_childcare_expenses = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        subsidies = spm_unit("child_care_subsidies", period)
        return max_(pre_subsidy_childcare_expenses - subsidies, 0)
