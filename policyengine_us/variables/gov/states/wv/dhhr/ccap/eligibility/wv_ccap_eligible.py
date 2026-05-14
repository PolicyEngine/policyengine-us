from policyengine_us.model_api import *


class wv_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia CCAP"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6766/download?inline#page=25",
        "https://bfa.wv.gov/media/39915/download?inline#page=16",
    )

    def formula(spm_unit, period, parameters):
        # We don't enforce a minimum parent-age floor: §1.1.10 recognizes
        # emancipated minors, §1.1.13 treats them as separate families, and
        # §4.5.3.6 / §4.5.6 explicitly contemplate minor parents in high
        # school or home schooling. The activity requirement below carries
        # the substantive caretaker check.
        has_eligible_child = add(spm_unit, period, ["wv_ccap_eligible_child"]) > 0
        income_eligible = spm_unit("wv_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("wv_ccap_activity_eligible", period)
        return has_eligible_child & income_eligible & asset_eligible & activity_eligible
