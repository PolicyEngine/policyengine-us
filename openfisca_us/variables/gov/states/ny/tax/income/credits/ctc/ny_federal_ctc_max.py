from openfisca_us.model_api import *


class ny_federal_ctc_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY federal CTC maximum"
    unit = USD
    documentation = "The version of the federal CTC used to determine the NY Empire State Child Credit, before limiting to tax liability."
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ctc = parameters(
            "2017-01-01"
        ).gov.irs.credits.ctc  # Uses pre-TCJA parameters
        count_children = add(tax_unit, period, ["is_ctc_qualifying_child"])
        filing_status = tax_unit("filing_status", period)
        maximum_amount = ctc.child.amount * count_children
        phase_out_threshold = ctc.phase_out.threshold[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        income_over_threshold = max_(0, agi - phase_out_threshold)
        reduction = income_over_threshold * ctc.phase_out.rate
        return max_(0, maximum_amount - reduction)
