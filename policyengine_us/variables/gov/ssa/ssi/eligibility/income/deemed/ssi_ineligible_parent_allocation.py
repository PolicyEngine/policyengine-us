from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status._ssi_parent_supplement import (
    _ssi_parent_supplement_level,
)


class ssi_ineligible_parent_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible parent allocation"
    unit = USD
    documentation = (
        "The part of an ineligible parent's income that SSI sets aside for the "
        "parents before deeming the rest to an eligible child."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1165#d_3",
        "https://www.law.cornell.edu/cfr/text/20/416.1166#e_1",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320630",
    )

    def formula(person, period, parameters):
        ssi = parameters(period).gov.ssa.ssi.amount
        ineligible_parent = person("is_ssi_ineligible_parent", period)
        count_ineligible_parents = person.tax_unit.sum(ineligible_parent)
        spouse = _ssi_spouse_index(person, period)
        has_spouse = spouse >= 0
        safe_spouse = np.maximum(spouse, 0)
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        pooled_with_spouse = (
            has_spouse
            & ineligible_parent[safe_spouse]
            & (tax_unit[safe_spouse] == tax_unit)
        )
        # 20 CFR 416.1165(d)(3)(i) subtracts the couple rate "if both parents live
        # with you" and (d)(3)(ii) the individual rate "if only one parent lives
        # with you". Two ineligible spouses in one tax unit, whose income is pooled
        # there, share the couple rate; a spouse filing elsewhere leaves all of it
        # to this parent. A parent whose spouse stays eligible also takes all of
        # it, which gives the result in 416.1166(e)(1): "If you are eligible for
        # SSI benefits after your spouse's income has been deemed to you, we do not
        # deem any income to your child."
        federal = (
            select(
                [pooled_with_spouse, has_spouse, count_ineligible_parents == 2],
                [ssi.couple / 2, ssi.couple, ssi.couple / 2],
                default=ssi.individual,
            )
            * MONTHS_IN_YEAR
        )
        # POMS SI 01320.630 B.1 deems from aged, blind or disabled parents only
        # "the countable income in excess of what is required to reduce the
        # parents' FBR and any Federally-administered State supplement to zero",
        # and 416.1166(e)(2) only the spouse's income "not used to reduce your SSI
        # benefits to zero". So the allowance adds the at-home supplement the
        # parent's own test used: the couple's in a shared pool or beside an
        # eligible spouse, and a lone parent's own.
        # For a lone parent, and for two such parents on a joint claim, 416.1165(d)(3)
        # names only the Federal benefit rate. PE takes the POMS reading there too,
        # as the project lead ruled on 2026-11-12 (candidate
        # us:ssi-parent-allowance-state-supplement): it avoids a jump in deemed
        # income where the parent's income passes the federal rate plus supplement.
        # NOTE: two unmarried flagged parents share the federal couple rate alone.
        level = _ssi_parent_supplement_level(person, period, parameters)
        couple_level = max_(level, level[safe_spouse] * has_spouse)
        supplement = select(
            [pooled_with_spouse, has_spouse, count_ineligible_parents == 2],
            [couple_level / 2, couple_level, 0],
            default=level,
        )
        return (federal + supplement) * ineligible_parent
