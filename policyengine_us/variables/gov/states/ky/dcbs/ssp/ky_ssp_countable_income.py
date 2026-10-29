from policyengine_us.model_api import *


class ky_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Kentucky SSP countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = (
        # 921 KAR 2:015 §8(8): "The SSI twenty (20) dollar general exclusion
        # shall not be an allowable deduction from income."
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        # OMVOLV MS 2300: "The $20 general exclusion from unearned income and
        # deductions for medical expenses are not allowed in State
        # Supplementation."
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLV.pdf#page=5",
    )

    def formula(person, period, parameters):
        # Mirror ssi_countable_income but skip the $20 general exclusion per
        # §8(8). The $65 earned exclusion and 50% earned share still apply.
        earned = max_(
            person("ssi_marital_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = (
            person("ssi_marital_unearned_income", period)
            + person("ssi_unearned_income_deemed_from_ineligible_parent", period)
            + person("ssi_in_kind_support_and_maintenance", period)
        )
        p = parameters(period).gov.ssa.ssi.income.exclusions
        countable_earned = max_(earned - p.earned, 0) * (1 - p.earned_share)
        personal_countable = unearned + countable_earned

        both_eligible = person("ssi_couple_computation_applies", period)
        spousal_deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
        # Same gate as ssi_countable_income: people who are not aged, blind or
        # disabled have no countable income of their own. KY SSP requires
        # is_ssi_eligible, so this does not change any payment.
        is_aged_blind_disabled = person("is_ssi_aged_blind_disabled", period.this_year)
        return where(
            ~is_aged_blind_disabled,
            0,
            where(
                both_eligible,
                personal_countable / 2,
                personal_countable + spousal_deemed,
            ),
        )
