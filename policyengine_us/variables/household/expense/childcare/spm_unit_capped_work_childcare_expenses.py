from policyengine_us.model_api import *


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"

    def formula(spm_unit, period, parameters):
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        # States where we model childcare subsidies.
        STATES_WITH_CHILD_CARE_SUBSIDIES = ["CA", "CO"]
        subsidy_variables = [
            i.lower() + "_child_care_subsidies"
            for i in STATES_WITH_CHILD_CARE_SUBSIDIES
        ]
        subsidies = add(spm_unit, period, subsidy_variables)
        return max_(pre_subsidy_childcare_expenses - subsidies, 0)
