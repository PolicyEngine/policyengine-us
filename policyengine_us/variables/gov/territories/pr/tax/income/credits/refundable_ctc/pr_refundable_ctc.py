from policyengine_us.model_api import *


class pr_refundable_ctc_social_security_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico refundable CTC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf"

    def formula(tax_unit, period, parameters):
        # line 24
        sum_eitc_ssi = add(
            tax_unit, period, ["eitc.py", max_(0, "uncapped_ssi.py")]
        )

        # line 25
        reduced_ss_tax = max_(
            0,
            tax_unit("pr_refundable_ctc_social_security_tax", period)
            - sum_eitc_ssi,
        )

        # line 26
        base_credit = max_(
            tax_unit("refundable_ctc.py", period), reduced_ss_tax
        )

        # line 27
        return min_(base_credit, tax_unit("ctc.py", period))
