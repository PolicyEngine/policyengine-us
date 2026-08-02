from policyengine_us.model_api import *


class is_snap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SNAP eligible"
    documentation = "Whether this SPM unit is eligible for SNAP benefits"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
    )

    def formula(spm_unit, period, parameters):
        net = spm_unit("meets_snap_net_income_test", period)
        gross = spm_unit("meets_snap_gross_income_test", period)
        asset = spm_unit("meets_snap_asset_test", period)
        normal_eligibility = net & gross & asset
        # Categorical eligibility (SSI, TANF, and BBCE TANF) overrides tests.
        categorical_eligibility = spm_unit("meets_snap_categorical_eligibility", period)
        person = spm_unit.members
        # At least one member must satisfy the student (7 USC 2015(e)),
        # immigration (7 USC 2015(f)), and work-requirement (7 CFR 273.7,
        # 273.24) rules simultaneously. Testing these conditions with
        # separate any() reductions would incorrectly pass a unit where
        # different members satisfy different rules with no single member
        # satisfying all of them; is_snap_excluded_member already encodes
        # the per-person disjunction of the three filters.
        eligible_member_present = spm_unit.any(
            ~person("is_snap_excluded_member", period)
        )
        return (normal_eligibility | categorical_eligibility) & eligible_member_present
