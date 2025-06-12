from policyengine_us.model_api import *


class pr_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf"
        "https://www.law.cornell.edu/uscode/text/26/24#h_4_A"
    )

    # This provision is part of the federal CTC legal code
    # will will merge the logic with the federal CTC once the puerto income tax structure is completed
    def formula(tax_unit, period, parameters):
        # line 24
        # uncapped_ssi can be below 0
        ssi = max_(0, add(tax_unit, period, ["uncapped_ssi"]))
        sum_eitc_ssi = add(tax_unit, period, ["eitc"]) + ssi

        # line 25
        reduced_ss_tax = max_(
            0,
            tax_unit("pr_refundable_ctc_social_security_tax", period)
            - sum_eitc_ssi,
        )

        # line 26
        base_credit = max_(tax_unit("refundable_ctc", period), reduced_ss_tax)

        # line 27
        return min_(base_credit, tax_unit("ctc", period))
