from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
)


class il_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.illinois.gov/programs/eitc.html",
        # 35 ILCS 5/212 bases the IL EIC on the federal IRC 32 credit.
        "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K212",
        # IRC 32(c)(3)(A) applies the IRC 152(c) qualifying-child definition.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_A",
        # IRC 32(c)(1)(A)(ii)(III): a filer without a qualifying child must not
        # be a dependent of another taxpayer.
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A_ii",
        # Publication 596: on a joint return, neither spouse may be claimable.
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
    )
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Same qualifying-child test as the federal eitc_child_count, with an
        # ITIN accepted in place of a Social Security number.
        qualifying_child = person("is_eitc_qualifying_child", period) & has_tin
        child_count = tax_unit.sum(qualifying_child)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        p = parameters(period).gov.states.il.tax.income.credits.eitc
        # The state extension waives only the identification and age rules. A
        # filer without a qualifying child still must not be a dependent of
        # another taxpayer (IRC 32(c)(1)(A)(ii)(III)); on a joint return
        # neither spouse may be (Publication 596).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        demographic_eligible = (child_count > 0) | (
            tax_unit.any(is_head_or_spouse & (age >= p.childless_min_age))
            & ~filer_is_dependent
        )
        state_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count,
            demographic_eligible,
            filer_has_tin,
        )
        match = parameters(period).gov.states.il.tax.income.credits.eitc.match
        return state_eitc * match
