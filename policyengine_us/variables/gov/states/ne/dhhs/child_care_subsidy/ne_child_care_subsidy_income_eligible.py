from policyengine_us.model_api import *


class ne_child_care_subsidy_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy program income eligible"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://dhhs.ne.gov/Pages/Child-Care-Parents.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.dhhs.child_care_subsidy.fpg_fraction
        income = add(spm_unit, period, ["adjusted_gross_income"])
        fpg = spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.initial_eligibility
        return income <= income_limit
