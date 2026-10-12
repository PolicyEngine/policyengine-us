from policyengine_us.model_api import *


class ctc_social_security_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable Child Tax Credit Social Security Tax"
    unit = USD
    documentation = (
        "Social Security taxes considered in the Child Tax Credit calculation: "
        "the head's and, on a joint return, the spouse's (Schedule 8812 "
        "Part II-B, lines 21 to 23, less the excess withheld on Schedule 3). "
        "Section 24(d)(2)(A) counts the taxpayer's own payroll taxes, so a "
        "tax unit dependent's payroll taxes, which are figured on the "
        "dependent's own wages and own return, are left out."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#d_2",
        "https://www.irs.gov/pub/irs-prior/f1040s8--2024.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/i1040s8--2024.pdf#page=9",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.ctc.refundable.social_security
        added = tax_unit_non_dep_add(tax_unit, period, p.add)
        subtracted = tax_unit_non_dep_add(tax_unit, period, p.subtract)
        return added - subtracted
