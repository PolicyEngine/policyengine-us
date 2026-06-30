from policyengine_us.model_api import *


class mi_ccap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan CDC"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=15"
    )

    def formula(spm_unit, period, parameters):
        # BEM 703: assess protective-services / income-waived groups first,
        # then the income-eligible group. All groups must pass the asset test
        # and have a valid need reason.
        has_eligible_child = add(spm_unit, period, ["mi_ccap_eligible_child"]) > 0
        income_waived = spm_unit("mi_ccap_income_waived", period)
        income_eligible = spm_unit("mi_ccap_income_eligible", period)
        asset_eligible = spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = spm_unit("mi_ccap_activity_eligible", period)
        return (
            has_eligible_child
            & (income_waived | income_eligible)
            & asset_eligible
            & activity_eligible
        )
