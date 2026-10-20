from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ia_ssa_care_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA care countable income without general disregard"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "Whole marital-group income for adult in-home care; individual income for other care. A child in in-home care receives income deemed from parents under the Iowa method. First-month spouse deeming and deductions absent from the federal SSI income inputs are not modeled."
    reference = (
        # 441 IAC 52.1(3)"a"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 34, 41-42, 49, 59-63
        "https://hhs.iowa.gov/media/3987/download?inline=#page=34",
    )

    def formula(person, period, parameters):
        category = person("ia_ssa_category", period)
        home = category == category.possible_values.IN_HOME_CARE
        joint = person("ssi_couple_computation_applies", period)
        adult = ~person("is_child", period.this_year)
        combine = where(home, adult & (person.marital_unit.nb_persons() == 2), joint)
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        # 6-B excludes one-third of child support a child receives from an
        # absent parent. Federal SSI does not apply 20 CFR 416.1124(c)(11) yet
        # (issue 10242), so the shared federal share is read here directly.
        unearned = max_(
            person("ssi_unearned_income", period)
            - person("interest_income", period)
            - person("dividend_income", period)
            - ~adult
            * person("child_support_received", period)
            * parameters(period).gov.ssa.ssi.income.exclusions.child_support_share,
            0,
        )
        # 6-B: "do not rely on SSI deeming calculations for children" in
        # in-home health-related care; other care uses SSI parental deeming.
        deemed = where(
            home,
            person("ia_ssa_income_deemed_from_parents", period),
            person("ssi_unearned_income_deemed_from_ineligible_parent", period),
        )
        unearned = unearned + ~adult * deemed
        benefit = person("ssi", period)
        earned = where(combine, person.marital_unit.sum(earned), earned)
        unearned = where(combine, person.marital_unit.sum(unearned), unearned)
        benefit = where(combine, person.marital_unit.sum(benefit), benefit)
        income = (
            _apply_ssi_exclusions(
                earned * MONTHS_IN_YEAR,
                unearned * MONTHS_IN_YEAR,
                parameters,
                period,
                general_exclusion=0,
            )
            / MONTHS_IN_YEAR
            + benefit
        )
        return where(combine & ~home, income / 2, income)
