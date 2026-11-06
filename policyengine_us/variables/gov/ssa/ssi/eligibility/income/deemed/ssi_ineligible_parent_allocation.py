from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class ssi_ineligible_parent_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible parent allocation"
    unit = USD
    documentation = "The amount of income that SSI does not to SSI claimants."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1165#d_3",
        "https://www.law.cornell.edu/cfr/text/20/416.1166#e_1",
    )

    def formula(person, period, parameters):
        ssi = parameters(period).gov.ssa.ssi.amount
        ineligible_parent = person("is_ssi_ineligible_parent", period)
        count_ineligible_parents = person.tax_unit.sum(ineligible_parent)
        spouse = _ssi_spouse_index(person, period)
        has_spouse = spouse >= 0
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        # 20 CFR 416.1165(d)(3)(i) subtracts the couple rate "if both parents live
        # with you" and (d)(3)(ii) the individual rate "if only one parent lives
        # with you". Two ineligible spouses in one tax unit, whose income is pooled
        # there, share the couple rate; a spouse filing elsewhere leaves all of it
        # to this parent. A parent whose spouse stays eligible also takes all of
        # it, which gives the result in 416.1166(e)(1): "If you are eligible for
        # SSI benefits after your spouse's income has been deemed to you, we do not
        # deem any income to your child."
        return (
            select(
                [
                    has_spouse
                    & ineligible_parent[spouse]
                    & (tax_unit[spouse] == tax_unit),
                    has_spouse,
                    count_ineligible_parents == 2,
                ],
                [ssi.couple / 2, ssi.couple, ssi.couple / 2],
                default=ssi.individual,
            )
            * MONTHS_IN_YEAR
            * ineligible_parent
        )
