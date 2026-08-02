from policyengine_us.model_api import *


class ne_child_care_subsidy_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy monthly federal poverty guideline"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=6",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
    )

    def formula(spm_unit, period, parameters):
        # Nebraska's subsidy standards sit on the § 68-1206(3) October rate
        # cycle; months before the update month use the prior year's FPG. The
        # published standards are rounded to whole dollars, but the regulation
        # attaches no rounding to the underlying guideline.
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        update_month = parameters(
            period
        ).gov.states.ne.dhhs.child_care_subsidy.fpg_update_month
        year = period.start.year
        if period.start.month < update_month:
            year -= 1
        p = parameters(f"{year}-{int(update_month):02d}-01").gov.hhs.fpg
        return (
            p.first_person[state_group] + p.additional_person[state_group] * (n - 1)
        ) / MONTHS_IN_YEAR
