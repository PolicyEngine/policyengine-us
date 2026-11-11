from policyengine_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        # On its sample invoices in an August 14, 2026 memo on prekindergarten
        # and CCFAP tuition (PDF pages 1 and 10), Vermont's Child Development
        # Division takes the state's payment off tuition.
        pre_subsidy_childcare_expenses = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        subsidies = spm_unit("child_care_subsidies", period)
        # A payment above one provider's bill stays with that provider and
        # pays none of another provider's bill.
        above_bills = spm_unit("child_care_subsidies_above_provider_bills", period)
        return max_(pre_subsidy_childcare_expenses - (subsidies - above_bills), 0)
