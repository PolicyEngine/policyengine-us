from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Nebraska Child Care Subsidy program"
    definition_period = MONTH
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=15",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=17",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        person = spm_unit.members
        eligible_parent = person("ne_child_care_subsidy_eligible_parent", period)
        eligible_child = person("ne_child_care_subsidy_eligible_child", period)
        eligible_child_present = spm_unit.sum(eligible_child) > 0
        income_eligible = spm_unit("ne_child_care_subsidy_income_eligible", period)
        if not p.provider_rate_model_in_effect:
            # Preserve the pre-matrix model path for historical periods.
            return (
                (spm_unit.sum(eligible_parent) > 0)
                & eligible_child_present
                & income_eligible
            )
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year) | person(
            "is_parent", period.this_year
        )
        all_caretakers_eligible = spm_unit.sum(caretaker & ~eligible_parent) == 0
        provider_eligible = person("ne_child_care_subsidy_provider_eligible", period)
        enrolled = spm_unit("ne_child_care_subsidy_enrolled", period)
        at_redetermination = spm_unit(
            "ne_child_care_subsidy_at_redetermination", period
        )
        activity_eligible = all_caretakers_eligible | (enrolled & ~at_redetermination)
        eligible_provider_child_present = (
            spm_unit.sum(eligible_child & provider_eligible) > 0
        )
        asset_eligible = spm_unit(
            "is_ccdf_asset_eligible", period.this_year
        ) | spm_unit("ne_child_care_subsidy_categorical_waived", period)
        asset_eligible |= enrolled & ~at_redetermination
        return (
            activity_eligible
            & eligible_provider_child_present
            & income_eligible
            & asset_eligible
        )
