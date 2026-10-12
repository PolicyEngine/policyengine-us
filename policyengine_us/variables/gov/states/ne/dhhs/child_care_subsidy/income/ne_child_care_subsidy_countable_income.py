from policyengine_us.model_api import *


class ne_child_care_subsidy_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nebraska Child Care Subsidy countable income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=11",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=3",
        "https://nebraskalegislature.gov/FloorDocs/109/PDF/Slip/LB304.pdf#page=1",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.dhhs.child_care_subsidy.income.earned_income_disregard
        gross_income = spm_unit("ne_child_care_subsidy_gross_income", period)
        gross_earned = spm_unit("ne_child_care_subsidy_gross_earned_income", period)
        # LB304 grants the disregard after 12 continuous months of receipt;
        # the enrollment flag is the observable proxy for that history.
        disregard_eligible = spm_unit("ne_child_care_subsidy_enrolled", period)
        disregard = where(disregard_eligible, max_(gross_earned, 0) * p.rate, 0)
        return max_(gross_income - disregard, 0)
