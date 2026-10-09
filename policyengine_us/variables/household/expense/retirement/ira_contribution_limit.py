from policyengine_us.model_api import *


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

        total_desired = add(
            person,
            period,
            [
                "traditional_ira_contributions_desired",
                "roth_ira_contributions_desired",
            ],
        )
        # Only the lower-compensation spouse can use the spousal rule. The
        # higher-compensation spouse's generated contributions therefore use
        # their own compensation limit. Calculate these without referring to
        # actual contributions, which depend on this limit through the scale.
        own_contributions = min_(
            max_(total_desired, 0), min_(dollar_limit, compensation)
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
