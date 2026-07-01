from policyengine_us.model_api import *


class cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit("cdcc_credit_limit", period)
        potential = tax_unit("cdcc_potential", period)
        # In 2021, the CDCC was refundable
        p = parameters(period).gov.irs.credits
        if "cdcc" in p.refundable:
            credit = potential
        else:
            credit = min_(credit_limit, potential)
        # IRC 21(e)(2): a married taxpayer may claim the credit only on a
        # joint return, unless 21(e)(4) treats them as unmarried: living
        # apart from their spouse while maintaining a home for a qualifying
        # individual. In this model, is_separated carries the living-apart
        # condition. The qualifying-individual test is 21(b)(1)'s own
        # (broader than 7703(b)'s "qualifying child" test used elsewhere for
        # head-of-household), so it also covers a disabled dependent who is
        # not a qualifying child (e.g. a disabled parent) even though such a
        # taxpayer doesn't get HEAD_OF_HOUSEHOLD filing status in this model.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        person = tax_unit.members
        separated = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated", period)
        )
        has_qualifying_dependent = tax_unit.any(
            person("is_cdcc_eligible", period) & person("is_tax_unit_dependent", period)
        )
        treated_as_unmarried = separated & has_qualifying_dependent
        excluded = separate & ~treated_as_unmarried
        return where(excluded, 0, credit)
