from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_dc_ctc() -> Reform:
    class dc_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "DC Child Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://lims.dccouncil.gov/downloads/LIMS/52461/Introduction/B25-0190-Introduction.pdf"
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.dc.ctc
            person = tax_unit.members
            age = person("age", period)
            age_eligible = age < p.age_threshold
            eligible_children = tax_unit.sum(age_eligible)
            capped_children = min_(eligible_children, p.child_cap)
            income = tax_unit("adjusted_gross_income", period)
            max_amount = p.amount * capped_children
            increment = p.reduction.increment
            reduction_per_increment = p.reduction.amount
            filing_status = tax_unit("filing_status", period)
            reduction_start = p.reduction.start[filing_status]
            excess = max_(income - reduction_start, 0)
            increments = np.ceil(excess / increment)
            reduction_amount = increments * reduction_per_increment
            return max_(0, max_amount - reduction_amount)

    class dc_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "DC refundable credits"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
            "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
        )
        defined_for = StateCode.DC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.dc.tax.income.credits
            previous_credits = add(tax_unit, period, p.refundable)
            ctc = tax_unit("dc_ctc", period)
            return ctc + previous_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(dc_ctc)
            self.update_variable(dc_refundable_credits)

    return reform


def create_dc_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_dc_ctc()

    p = parameters.gov.contrib.states.dc.ctc

    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            return create_dc_ctc()
        current_period = current_period.offset(1, "year")
    return None


dc_ctc = create_dc_ctc_reform(None, None, bypass=True)
