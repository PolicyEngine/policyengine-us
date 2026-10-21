from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.retirement._ira_supplied_contributions import (
    supplied_ira_contributions,
)


class ira_contribution_limit(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution limit"
    unit = USD
    documentation = (
        "Combined traditional and Roth IRA contribution limit, including the "
        "dollar and compensation limits and compensation sharing for the "
        "lower-compensation spouse on a joint return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b_1",
        "https://www.law.cornell.edu/uscode/text/26/219#c",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
        "https://www.irs.gov/publications/p590a",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions
        catch_up_eligible = person("age", period) >= p.catch_up.age_threshold
        dollar_limit = p.limit.ira + where(catch_up_eligible, p.catch_up.limit.ira, 0)
        compensation = person("ira_compensation", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        joint = person.tax_unit("tax_unit_is_joint", period)
        joint_compensation = person.tax_unit.sum(compensation * head_or_spouse)
        spouse_compensation = where(
            head_or_spouse, joint_compensation - compensation, 0
        )

        own_limit = min_(dollar_limit, compensation)
        # Supplied actual contributions consume compensation as given:
        # traditional amounts up to this person's own limit, Roth amounts in
        # full, as in traditional_ira_deduction. Generated contributions then
        # fill only what remains of the person's own limit.
        supplied = supplied_ira_contributions(person, period)
        supplied_traditional = supplied["traditional_ira_contributions"]
        supplied_roth = supplied["roth_ira_contributions"]
        supplied_consumed = 0
        generated_desired = 0
        if supplied_traditional is None:
            generated_desired = generated_desired + person(
                "traditional_ira_contributions_desired", period
            )
        else:
            supplied_consumed = supplied_consumed + min_(
                max_(supplied_traditional, 0), own_limit
            )
        if supplied_roth is None:
            generated_desired = generated_desired + person(
                "roth_ira_contributions_desired", period
            )
        else:
            supplied_consumed = supplied_consumed + max_(supplied_roth, 0)
        # Only the lower-compensation spouse can use the spousal rule. The
        # higher-compensation spouse's generated contributions therefore use
        # their own compensation limit. Generated amounts are calculated
        # without referring to actual contributions, which depend on this
        # limit through the scale.
        own_contributions = supplied_consumed + min_(
            max_(generated_desired, 0), max_(own_limit - supplied_consumed, 0)
        )
        joint_own_contributions = person.tax_unit.sum(
            own_contributions * head_or_spouse
        )
        spouse_contributions = where(
            head_or_spouse, joint_own_contributions - own_contributions, 0
        )
        use_spousal_rule = joint & head_or_spouse & (compensation < spouse_compensation)
        spousal_compensation = compensation + max_(
            spouse_compensation - spouse_contributions, 0
        )
        compensation_limit = where(use_spousal_rule, spousal_compensation, compensation)
        return min_(dollar_limit, compensation_limit)
