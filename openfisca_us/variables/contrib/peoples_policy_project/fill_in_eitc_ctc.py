from openfisca_us.model_api import *


class fill_in_eitc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax credit filling in the phase-in of the EITC and CTC"
    unit = USD
    reference = "https://www.peoplespolicyproject.org/projects/extending-child-benefits"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Only calculate if active.
        if not parameters(
            period
        ).contrib.peoples_policy_project.fill_in_eitc_ctc:
            return 0
        eitc = tax_unit("eitc", period)
        eitc_maximum = tax_unit("eitc_maximum", period)
        eitc_reduction = tax_unit("eitc_reduction", period)
        eitc_fill_in = (eitc_maximum - eitc_reduction) - eitc

        ctc_maximum = tax_unit("ctc_maximum", period)
        ctc_reduction = tax_unit("ctc_reduction", period)
        ctc_limiting_tax_liability = tax_unit(
            "ctc_limiting_tax_liability", period
        )
        refundable_ctc = tax_unit("refundable_ctc", period)
        non_refundable_ctc = tax_unit("non_refundable_ctc", period)
        ctc_value_received = refundable_ctc + min_(
            non_refundable_ctc, ctc_limiting_tax_liability
        )
        ctc_fill_in = (ctc_maximum - ctc_reduction) - ctc_value_received

        return eitc_fill_in + ctc_fill_in
