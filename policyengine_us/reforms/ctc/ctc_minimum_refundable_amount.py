from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ctc_minimum_refundable_amount() -> Reform:
    class ctc_minimum_refundable_amount(Variable):
        value_type = float
        entity = Person
        label = "CTC minimum refundable amount"
        unit = USD
        defined_for = "ctc_qualifying_child"
        documentation = "Minimum refundable amount per child, exempt from phase-in but subject to phase-out."
        definition_period = YEAR

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.ctc.minimum_refundable

            age = person("age", period)

            return p.amount.calc(age)

    class refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "refundable CTC"
        unit = USD
        documentation = (
            "The portion of the Child Tax Credit that is refundable."
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

        def formula(tax_unit, period, parameters):
            # This line corresponds to "the credit which would be allowed under this section [the CTC section]"
            # without regard to this subsection [the refundability section] and the limitation under
            # section 26(a) [the section that limits the amount of the non-refundable CTC to tax liability].
            # This is the full CTC. This is then limited to the maximum refundable amount per child as per the
            # TCJA provision.

            ctc = parameters(period).gov.irs.credits.ctc

            maximum_amount = tax_unit("ctc_refundable_maximum", period)
            print(maximum_amount)

            total_ctc = tax_unit("ctc", period)
            print(total_ctc)

            if ctc.refundable.fully_refundable:
                reduction = tax_unit("ctc_phase_out", period)
                reduced_max_amount = max_(0, maximum_amount - reduction)
                return min_(reduced_max_amount, total_ctc)

            maximum_refundable_ctc = min_(maximum_amount, total_ctc)
            print(maximum_refundable_ctc)
            minimum_refundable_ctc = add(
                tax_unit, period, ["ctc_minimum_refundable_amount"]
            )
            phase_in = tax_unit("ctc_phase_in", period)
            print(phase_in)
            phase_in_with_minimum = max_(phase_in, minimum_refundable_ctc)
            print(phase_in_with_minimum)
            limiting_tax = tax_unit("ctc_limiting_tax_liability", period)
            ctc_capped_by_tax = min_(total_ctc, limiting_tax)
            ctc_capped_by_increased_tax = min_(
                total_ctc, limiting_tax + phase_in_with_minimum
            )
            amount_ctc_would_increase = (
                ctc_capped_by_increased_tax - ctc_capped_by_tax
            )
            return min_(maximum_refundable_ctc, amount_ctc_would_increase)

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_minimum_refundable_amount)
            self.update_variable(refundable_ctc)

    return reform


def create_ctc_minimum_refundable_amount_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_minimum_refundable_amount()

    p = parameters.gov.contrib.ctc.minimum_refundable

    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_minimum_refundable_amount()
    else:
        return None


ctc_minimum_refundable_amount = create_ctc_minimum_refundable_amount_reform(
    None, None, bypass=True
)
