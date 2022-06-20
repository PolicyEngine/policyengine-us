from openfisca_us.model_api import *


class is_snap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SNAP eligible"
    documentation = "Whether this SPM unit is eligible for SNAP benefits"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        net = spm_unit("meets_snap_net_income_test", period)
        gross = spm_unit("meets_snap_gross_income_test", period)
        asset = spm_unit("meets_snap_asset_test", period)
        normal_eligibility = net & gross & asset
        # Categorical eligibility (SSI, TANF, and BBCE TANF) overrides tests.
        categorical_eligibility = spm_unit(
            "meets_snap_categorical_eligibility", period
        )
        return normal_eligibility | categorical_eligibility
