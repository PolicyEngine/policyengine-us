from policyengine_us.model_api import *


class cdcc_filing_status_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filing status eligible for the Child/dependent care credit"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#e_2",
        "https://www.law.cornell.edu/uscode/text/26/21#e_4",
    )

    def formula(tax_unit, period, parameters):
        # IRC 21(e)(2): a married taxpayer may claim the credit only on a
        # joint return, unless 21(e)(4) treats them as unmarried.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        treated_as_unmarried = tax_unit("cdcc_treated_as_unmarried", period)
        return ~separate | treated_as_unmarried
