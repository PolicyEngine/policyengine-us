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
        # Nebraska publishes updated subsidy standards each October. Months
        # before October therefore continue to use the prior year's FPG.
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.hhs.fpg
        return (
            p.first_person[state_group] + p.additional_person[state_group] * (n - 1)
        ) / MONTHS_IN_YEAR
