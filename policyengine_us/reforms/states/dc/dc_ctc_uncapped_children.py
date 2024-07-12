from policyengine_us.model_api import *


def create_dc_ctc_uncapped_children() -> Reform:
    class dc_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "DC Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://lims.dccouncil.gov/downloads/LIMS/52461/Introduction/B25-0190-Introduction.pdf"
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.dc.tax.income.credits.ctc
            eligible_children = tax_unit("ctc_qualifying_children", period)
            income = tax_unit("adjusted_gross_income", period)
            max_amount = p.amount * eligible_children
            increment = p.reduction.increment
            reduction_per_increment = p.reduction.amount
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            reduction_start = where(
                joint, p.reduction.start.joint, p.reduction.start.single
            )
            excess = max_(income - reduction_start, 0)
            increments = np.ceil(excess / increment)
            reduction_amount = increments * reduction_per_increment
            return max_(0, max_amount - reduction_amount)

    class reform(Reform):
        def apply(self):
            self.update_variable(dc_ctc)

    return reform


def create_dc_ctc_uncapped_children_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_dc_ctc_uncapped_children()

    p = parameters(period).gov.contrib.states.dc.ctc_uncapped_children

    if p.in_effect:
        return create_dc_ctc_uncapped_children()
    else:
        return None


dc_ctc_uncapped_children = create_dc_ctc_uncapped_children_reform(
    None, None, bypass=True
)
