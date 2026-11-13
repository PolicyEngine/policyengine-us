from policyengine_us.model_api import *


class pr_refundable_ctc_social_security_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Puerto Rico social security and medicare taxes for refundable Child Tax Credit"
    )
    documentation = (
        "The head's and, on a joint return, the spouse's social security and "
        "Medicare taxes. Section 24(d)(2)(A) counts the taxpayer's own "
        "payroll taxes, so a tax unit dependent's are left out."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf",
        "https://www.law.cornell.edu/uscode/text/26/24#h_4_A",
        "https://www.law.cornell.edu/uscode/text/26/24#d_2",
    )

    # line 23
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.ctc.refundable.social_security
        return tax_unit_non_dep_add(tax_unit, period, p.add)
