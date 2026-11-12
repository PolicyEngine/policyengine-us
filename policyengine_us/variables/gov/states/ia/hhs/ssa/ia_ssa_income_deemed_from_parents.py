from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed.ssi_resources_deemed_from_ineligible_parent import (
    _ssi_parental_resource_pool,
)


class ia_ssa_income_deemed_from_parents(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA in-home health-related care income deemed from parents"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    reference = (
        # PDF pages 46-49
        "https://hhs.iowa.gov/media/3987/download?inline=#page=46",
        # 441 IAC 177.2(1)"g"(1)
        "https://www.legis.iowa.gov/docs/iac/chapter/441.177.pdf#page=2",
        # 441 IAC 177.4(1)"g"(1) (IAC 2/5/25)
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2",
    )

    def formula(person, period, parameters):
        # 6-B: "The procedures for deeming from a parent to a child under
        # in-home health-related care differ from the SSI program", so the
        # Iowa method replaces SSI parental income deeming for these children.
        # The deemors are the co-resident parents and each parent's
        # co-resident spouse, as for parental resources; a parent who receives
        # SSI is not a deemor.
        # NOTE: The manual and the rule it cites deduct the unmet medical needs
        # of the parents and ineligible children, which are not modeled.
        # NOTE: 6-B p.47: "For parents with earned income only, allow the
        # following deductions before deeming income to the eligible child: $65
        # work expense. Double the SSI allowance". 441 IAC 177 lists only "an
        # additional basic SSI standard" when all income is earned, with no $65:
        # 177.4(1)"g"(1) in the IAC 2/5/25 edition and 177.2(1)"g"(1) after ARC
        # 0460D (IAC 8/5/26, effective October 1, 2026), so the conflict covers
        # all of 2026. The model follows the manual
        # (ia_ssa_income_deemed_from_parents.yaml Cases 2-3).
        ssi = parameters(period).gov.ssa.ssi
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        earned = where(receives_ssi, 0, person("ssi_earned_income", period))
        unearned = where(receives_ssi, 0, person("ssi_unearned_income", period))
        parental_earned, parent_count, pool = _ssi_parental_resource_pool(
            person, period, earned
        )
        parental_unearned, _, _ = _ssi_parental_resource_pool(person, period, unearned)
        # 6-B, Home Maintenance Allowance (IHHRC): the 6-B allowances equal the
        # SSI individual, couple and dependent standards, so an SSI reform
        # carries over to Iowa.
        # NOTE: As in resources deeming, the allowance follows the number of
        # co-resident deemors including a parent who receives SSI, so one SSI
        # parent with an ineligible parent gives the couple allowance. Federal
        # ssi_ineligible_parent_allocation counts only ineligible parents; 6-B
        # and 441 IAC 177 are silent on this case.
        allowance = where(parent_count > 1, ssi.amount.couple, ssi.amount.individual)
        pool_count = int(np.max(pool, initial=-1)) + 1
        # NOTE: 441 IAC 177.4(1)"g"(1)2 (IAC 2/5/25; 177.2(1)"g"(1)2 from
        # October 1, 2026) disregards "The amount of the basic supplemental
        # security income standard for a dependent for each ineligible child in
        # the home". 6-B pp.47-49 allow a "maximum of $497 per child" and
        # "Subtract any income of the dependent from the maximum deduction"
        # (E family: $347 per child). The model follows the manual
        # (ia_ssa_income_deemed_from_parents.yaml Case 3).
        # Each ineligible child of the same parents adds the SSI dependent
        # standard less that child's own income.
        sibling_allowance = np.bincount(
            pool,
            weights=person("ssi_ineligible_child_allocation", period),
            minlength=pool_count,
        )[pool]
        exclusions = ssi.income.exclusions
        has_earned = parental_earned > 0
        has_unearned = parental_unearned > 0
        remaining_earned = max_(parental_earned - exclusions.earned, 0)
        # All earned: $65 and a second SSI standard for the parents. Earned and
        # unearned: $65 plus one-half of the remaining earnings. All unearned:
        # no earnings deduction.
        countable = select(
            [has_earned & has_unearned, has_earned],
            [
                remaining_earned * (1 - exclusions.earned_share) + parental_unearned,
                remaining_earned - allowance,
            ],
            default=parental_unearned,
        )
        deemed = max_(countable - allowance - sibling_allowance, 0)
        # The Iowa sources are silent on several eligible children; divide
        # equally among the blind or disabled children of the same parents, as
        # SSI does.
        eligible_child = person("is_ssi_aged_blind_disabled", period.this_year) & (
            person("is_child", period.this_year)
        )
        children = np.bincount(
            pool, weights=eligible_child.astype(float), minlength=pool_count
        )[pool]
        return eligible_child * deemed / max_(children, 1)
