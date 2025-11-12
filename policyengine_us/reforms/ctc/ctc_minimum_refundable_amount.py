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

            maximum_amount = tax_unit("ctc_refundable_maximum", period)
            total_ctc = tax_unit("ctc", period)

            maximum_refundable_ctc = min_(maximum_amount, total_ctc)
            minimum_refundable_ctc = add(
                tax_unit, period, ["ctc_minimum_refundable_amount"]
            )
            phase_in = tax_unit("ctc_phase_in", period)

            phase_in_with_minimum = phase_in + minimum_refundable_ctc
            ctc_capped_by_increased_tax = min_(
                total_ctc, phase_in_with_minimum
            )

            return min_(maximum_refundable_ctc, ctc_capped_by_increased_tax)

    class ctc_refundable_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum refundable CTC"
        unit = USD
        documentation = "The maximum refundable CTC for this person."
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/24#a",
            "https://www.law.cornell.edu/uscode/text/26/24#h",
            "https://www.law.cornell.edu/uscode/text/26/24#i",
            "https://www.irs.gov/pub/irs-prior/f1040--2021.pdf",
            "https://www.irs.gov/pub/irs-prior/f1040s8--2021.pdf",
        )

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            # Use either normal or ARPA CTC maximums.
            individual_max = person("ctc_child_individual_maximum", period)
            arpa_max = person("ctc_child_individual_maximum_arpa", period)
            child_amount = tax_unit.sum(individual_max + arpa_max)
            ctc = parameters(period).gov.irs.credits.ctc
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            refundable_max = (
                ctc.refundable.individual_max * qualifying_children
            )
            return min_(child_amount, refundable_max)

    class non_refundable_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "non-refundable CTC"
        unit = USD
        documentation = (
            "The portion of the Child Tax Credit that is not refundable."
        )
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            return 0

    class ctc_value(Variable):
        value_type = float
        entity = TaxUnit
        label = "CTC value"
        unit = USD
        documentation = "Actual value of the Child Tax Credit"
        definition_period = YEAR

        adds = ["refundable_ctc"]

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_minimum_refundable_amount)
            self.update_variable(refundable_ctc)
            self.update_variable(ctc_value)
            self.update_variable(ctc_refundable_maximum)
            self.update_variable(non_refundable_ctc)

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
