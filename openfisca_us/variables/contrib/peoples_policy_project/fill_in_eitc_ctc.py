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
        # Start with EITC fill-in.
        eitc = tax_unit("eitc", period)
        eitc_maximum = tax_unit("eitc_maximum", period)
        eitc_reduction = tax_unit("eitc_reduction", period)
        eitc_fill_in = max_(eitc_maximum - eitc_reduction, 0) - eitc
        # Add CTC fill-in based on value received.
        ctc_maximum = tax_unit("ctc_maximum", period)
        ctc_reduction = tax_unit("ctc_reduction", period)
        ctc_value_received = tax_unit("ctc_value_received", period)
        ctc_fill_in = max_(ctc_maximum - ctc_reduction, 0) - ctc_value_received
        # TODO: Calculate the maximum of the combined credits.
        return max_(eitc_fill_in + ctc_fill_in, 0)
