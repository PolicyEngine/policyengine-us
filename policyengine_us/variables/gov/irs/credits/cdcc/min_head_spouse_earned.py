from policyengine_us.model_api import *


class min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Less of head and spouse's earnings"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.cdcc
        is_joint = tax_unit("tax_unit_is_joint", period)
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        floor_eligible = person("cdcc_income_floor_eligible", period)

        head_earnings = tax_unit("head_earned", period)
        spouse_earnings = tax_unit("spouse_earned", period)
        head_floor_eligible = tax_unit.sum(is_head * floor_eligible) > 0
        spouse_floor_eligible = tax_unit.sum(is_spouse * floor_eligible) > 0

        # IRC section 21(d)(2): a spouse who is a student or incapable of
        # self-care is deemed to earn at least this floor, but only one spouse
        # may be deemed. Deem whichever eligible spouse yields the larger
        # lesser-of-earnings, leaving the other spouse's actual earnings.
        qualifying_individuals = tax_unit("count_cdcc_eligible", period)
        floor = p.deemed_earned_income.calc(qualifying_individuals)
        no_deem = min_(head_earnings, spouse_earnings)
        deem_head = where(
            head_floor_eligible,
            min_(max_(head_earnings, floor), spouse_earnings),
            0,
        )
        deem_spouse = where(
            spouse_floor_eligible,
            min_(max_(spouse_earnings, floor), head_earnings),
            0,
        )
        joint_earnings = max_(no_deem, max_(deem_head, deem_spouse))

        return where(is_joint, joint_earnings, tax_unit("head_earned", period))
