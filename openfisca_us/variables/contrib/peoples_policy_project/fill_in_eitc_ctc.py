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
        current_eitc_ctc = add(tax_unit, period, ["eitc", "ctc"])
        maximum_eitc_ctc = add(
            tax_unit, period, ["eitc_maximum", "ctc_maximum"]
        )
        # Subtract the phase-out reductions so it only fills in the
        # phase-in.
        phase_out_reductions = add(
            tax_unit, period, ["eitc_reduction", "ctc_reduction"]
        )
        return max_(
            0, maximum_eitc_ctc - current_eitc_ctc - phase_out_reductions
        )
