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
        # At least one member must be BOTH an eligible (non-ineligible) student
        # (7 USC 2015(e)) AND immigration-status eligible (7 USC 2015(f)).
        # Testing these two conditions with
        # separate any() reductions would incorrectly pass a unit where one
        # member satisfies the student rule and a different member satisfies
        # the immigration rule, with no single member satisfying both.
        eligible_member_present = spm_unit.any(
            ~person("is_snap_ineligible_student", period.this_year)
            & person("is_snap_immigration_status_eligible", period)
        )
        work_requirements_eligibility = spm_unit("meets_snap_work_requirements", period)
        return (
            (normal_eligibility | categorical_eligibility)
            & eligible_member_present
            & work_requirements_eligibility
        )
