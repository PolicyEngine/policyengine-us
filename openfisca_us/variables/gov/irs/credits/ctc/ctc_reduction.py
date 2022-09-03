from openfisca_us.model_api import *
from openfisca_us.variables.gov.irs.credits.ctc.maximum.individual.ctc_child_individual_maximum import (
    ctc_child_individual_maximum,
)
from openfisca_us.variables.gov.irs.credits.ctc.maximum.individual.ctc_adult_individual_maximum import (
    ctc_adult_individual_maximum,
)
from openfisca_us.parameters import default_parameters


class ctc_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC reduction from income"
    unit = USD
    documentation = "Reduction of the total CTC due to income."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        ctc = parameters(period).gov.irs.credits.ctc
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        income_over_threshold = max_(0, income - phase_out_threshold)
        reduction = ctc.phase_out.rate * income_over_threshold
        maximum_ctc = tax_unit("ctc_maximum", period)
        return min_(reduction, maximum_ctc)

    # TCJA's phase-out changes are purely parametric so don't require structural reform.

    def formula_2021(tax_unit, period, parameters):
        # The ARPA CTC has two phase-outs: the original, and a new phase-out
        # applying before and only to the increase in the maximum CTC under ARPA.

        income = tax_unit("adjusted_gross_income", period)
        ctc = parameters(period).gov.irs.credits.ctc
        filing_status = tax_unit("filing_status", period)
        phase_out_threshold = tax_unit("ctc_phase_out_threshold", period)
        income_over_threshold = max_(0, income - phase_out_threshold)
        reduction = ctc.phase_out.rate * income_over_threshold
        maximum_ctc = tax_unit("ctc_maximum", period)

        # Calculate the original phase-out
        original_phase_out = min_(reduction, maximum_ctc)

        # Calculate the income used to assess the new phase-out
        income_over_arpa_threshold = max_(
            0, income - ctc.phase_out.arpa.threshold[filing_status]
        )
        arpa_phase_out_max_reduction = (
            ctc.phase_out.arpa.rate * income_over_arpa_threshold
        )

        # Calculate the increase - do this by finding the original CTC if
        # ARPA had not applied - this year's variables, last year's parameters.
        no_arpa_parameters = default_parameters.clone()
        old_ctc = parameters(period.last_year).gov.irs.credits.ctc
        no_arpa_ctc = no_arpa_parameters.gov.irs.credits.ctc
        no_arpa_ctc.child.young.increase.update(value=0, period=period)
        no_arpa_ctc.child.amount.update(
            value=old_ctc.child.amount, period=period
        )

        ctc_without_arpa = tax_unit.sum(
            ctc_child_individual_maximum.formula(
                tax_unit.members, period, no_arpa_parameters
            )
            + ctc_adult_individual_maximum.formula_2018(
                tax_unit.members, period, no_arpa_parameters
            )
        )

        arpa_increase = maximum_ctc - ctc_without_arpa

        arpa_phase_out_range = (
            phase_out_threshold - ctc.phase_out.arpa.threshold[filing_status]
        )

        # Apply the phase-out
        arpa_reduction_max = min_(
            arpa_increase,
            ctc.phase_out.arpa.rate * arpa_phase_out_range,
        )

        arpa_reduction = min_(arpa_phase_out_max_reduction, arpa_reduction_max)

        return min_(original_phase_out + arpa_reduction, maximum_ctc)

    formula_2022 = formula
