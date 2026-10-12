from policyengine_us.model_api import *


class la_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Louisiana CCAP"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["la_ccap_eligible_child"]) > 0
        # LAC 28:CLXV.505: categorically eligible households skip the income
        # and activity tests of §509.
        categorical = spm_unit("la_ccap_categorically_eligible", period)
        income_eligible = spm_unit("la_ccap_income_eligible", period)
        activity_eligible = spm_unit("la_ccap_activity_eligible", period)
        # The $1,000,000 asset limit follows the federal CCDF standard
        # (CCDF State Plan §2.2.6) and is not waived for any pathway.
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        return (
            has_eligible_child
            & asset_eligible
            & (categorical | (income_eligible & activity_eligible))
        )
