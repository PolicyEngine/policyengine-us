from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_family_security_act_2_0_ctc() -> Reform:
    class ctc_phase_in_rate(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Child Tax Credit phase-in rate"

        def formula(tax_unit, period, parameters):
            income = tax_unit("adjusted_gross_income", period)
            p = parameters(
                period
            ).gov.contrib.congress.romney.family_security_act_2_0.ctc.phase_in
            return min_(income / p.income_phase_in_end, 1)

    class ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Child Tax Credit"
        unit = USD
        documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#a"

        def formula(tax_unit, period, parameters):
            maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
            phase_in_rate = tax_unit("ctc_phase_in_rate", period)
            phased_in_max_amont = maximum_amount * phase_in_rate
            reduction = tax_unit("ctc_phase_out", period)
            return max_(0, phased_in_max_amont - reduction)

    class ctc_child_individual_maximum(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child)"
        unit = USD
        documentation = (
            "The CTC entitlement in respect of this person as a child."
        )
        definition_period = YEAR
        reference = (
            "https://www.law.cornell.edu/uscode/text/26/24#a",
            "https://www.law.cornell.edu/uscode/text/26/24#h",
            "https://www.law.cornell.edu/uscode/text/26/24#i",
        )
        defined_for = "is_tax_unit_dependent"

        def formula(person, period, parameters):
            age = person("age", period)
            p = parameters(
                period
            ).gov.contrib.congress.romney.family_security_act_2_0.ctc
            return p.base.calc(age)

    class ctc_qualifying_children(Variable):
        value_type = int
        entity = TaxUnit
        label = "CTC-qualifying children"
        documentation = (
            "Count of children that qualify for the Child Tax Credit"
        )
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#c"

        def formula(tax_unit, period, parameters):
            total_children = tax_unit.sum(
                tax_unit.members("ctc_qualifying_child", period)
            )
            p = parameters(
                period
            ).gov.contrib.congress.romney.family_security_act_2_0.ctc
            return min_(total_children, p.child_cap)

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_phase_in_rate)
            self.update_variable(ctc)
            self.update_variable(ctc_qualifying_children)
            self.update_variable(ctc_child_individual_maximum)

    return reform


def create_family_security_act_2_0_ctc_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_family_security_act_2_0_ctc()

    # Look ahead for the next five years
    p = parameters.gov.contrib.congress.romney.family_security_act_2_0.ctc
    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).apply_ctc_structure:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_family_security_act_2_0_ctc()
    else:
        return None


family_security_act_2_0_ctc = create_family_security_act_2_0_ctc_reform(
    None, None, bypass=True
)
