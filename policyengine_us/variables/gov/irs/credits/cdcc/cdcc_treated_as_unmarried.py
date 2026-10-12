from policyengine_us.model_api import *


class cdcc_treated_as_unmarried(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Separate filer treated as unmarried for the child and dependent care credit"
    )
    documentation = (
        "Whether a married taxpayer filing a separate return is not considered "
        "married under IRC section 21(e)(4). Section 129(a)(2)(C) applies the "
        "same rule to the dependent care assistance exclusion cap."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#e_4",
        "https://www.law.cornell.edu/uscode/text/26/129#a_2_C",
    )

    def formula(tax_unit, period, parameters):
        # IRC 21(e)(4): a married individual filing a separate return is not
        # considered married when living apart from their spouse while
        # maintaining a home for a qualifying individual. In this model,
        # is_separated carries the living-apart condition; we don't track
        # 21(e)(4)(B)'s requirement that the spouse be absent during the last
        # six months of the year, or 21(e)(4)(A)'s requirements that the home
        # be the qualifying individual's principal abode for more than half
        # the year and that the taxpayer furnish over half the cost of
        # maintaining it, at the moment.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        person = tax_unit.members
        separated = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated", period)
        )
        # 21(e)(4)(A)(i) requires the home be the principal abode of a
        # qualifying individual under 21(b)(1) — including, via 21(e)(5), a
        # child of separated parents whom the other parent claims as a
        # dependent. The spouse prong (21(b)(1)(C)) cannot satisfy it for a
        # filer living apart from their spouse, so restrict to members other
        # than the head and spouse.
        qualifying_individual_in_home = tax_unit.any(
            person("is_cdcc_eligible", period)
            & ~person("is_tax_unit_head_or_spouse", period)
        )
        return separate & separated & qualifying_individual_in_home
