from policyengine_us.model_api import *


class ne_child_care_subsidy_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy program income eligible"
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://nebraskalegislature.gov/FloorDocs/109/PDF/Slip/LB304.pdf#page=1",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        income = spm_unit("ne_child_care_subsidy_countable_income", period)
        fpg = spm_unit("ne_child_care_subsidy_fpg", period)
        smi = spm_unit("ne_child_care_subsidy_smi", period)
        enrolled = spm_unit("ne_child_care_subsidy_enrolled", period)
        at_redetermination = spm_unit(
            "ne_child_care_subsidy_at_redetermination", period
        )
        initial_limit = np.ceil(fpg * p.fpg_fraction.initial_eligibility)
        redetermination_limit = np.ceil(fpg * p.fpg_fraction.redetermination)
        # Nebraska rounds the published 85% SMI column to the nearest
        # dollar, unlike the FPL columns, which round up.
        current_period_limit = np.round(smi * p.smi_fraction.current_period_exit)
        initial_eligible = income <= initial_limit
        redetermination_eligible = income < redetermination_limit
        current_period_eligible = income <= current_period_limit
        categorical = spm_unit("ne_child_care_subsidy_categorical_waived", period)
        return categorical | select(
            [at_redetermination, enrolled],
            [redetermination_eligible, current_period_eligible],
            default=initial_eligible,
        )
