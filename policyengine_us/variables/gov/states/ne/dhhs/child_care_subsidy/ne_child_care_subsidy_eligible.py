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
        person = spm_unit.members
        eligible_parent = person("ne_child_care_subsidy_eligible_parent", period)
        caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        all_caretakers_eligible = spm_unit.sum(caretaker & ~eligible_parent) == 0
        eligible_child = person("ne_child_care_subsidy_eligible_child", period)
        provider_eligible = person("ne_child_care_subsidy_provider_eligible", period)
        eligible_child_present = spm_unit.sum(eligible_child & provider_eligible) > 0
        income_eligible = spm_unit("ne_child_care_subsidy_income_eligible", period)
        asset_eligible = spm_unit(
            "is_ccdf_asset_eligible", period.this_year
        ) | spm_unit("ne_child_care_subsidy_categorical_waived", period)
        return (
            all_caretakers_eligible
            & eligible_child_present
            & income_eligible
            & asset_eligible
        )
