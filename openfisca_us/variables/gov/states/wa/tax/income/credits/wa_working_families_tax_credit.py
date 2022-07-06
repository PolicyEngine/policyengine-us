from openfisca_us.model_api import *


class wa_working_families_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://app.leg.wa.gov/RCW/default.aspx?cite=82.08.0206"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit
        claims_eitc = tax_unit("eitc", period) > 0
        # Parameters are based on EITC-eligible children.
        # TODO: Include ITIN children.
        eitc_child_count = tax_unit("eitc_child_count", period)
        max_amount = p.amount.calc(eitc_child_count)
        # WFTC phases out at a certain amount below the EITC phase-out start.
        eitc_phase_out_start = tax_unit("eitc_phase_out_start", period)
        phase_out_start_reduction = p.phase_out.start.calc(eitc_child_count)
        phase_out_start = eitc_phase_out_start - phase_out_start_reduction
        phase_out_rate = p.phase_out.rate.calc(eitc_child_count)
        earnings = tax_unit("filer_earned", period)
        excess = max_(0, earnings - phase_out_start)
        reduction = max_(0, excess * phase_out_rate)
        phased_out_amount = max_amount - reduction
        # Minimum benefit applies if calculated amount exceeds zero.
        amount_if_eligible = where(
            phased_out_amount > 0, max_(p.min_amount, phased_out_amount), 0
        )
        return amount_if_eligible * claims_eitc
