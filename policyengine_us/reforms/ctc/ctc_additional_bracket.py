from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ctc_additional_bracket() -> Reform:
    class ctc_child_individual_maximum(Variable):
        value_type = float
        entity = Person
        label = "CTC maximum amount (child) with additional bracket"
        unit = USD
        definition_period = YEAR
        defined_for = "is_tax_unit_dependent"

        def formula(person, period, parameters):
            age = person("age", period)
            p = parameters(period).gov.contrib.ctc.additional_bracket.amount
            return p.base.calc(age)

    class ctc_refundable_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum refundable CTC"
        unit = USD
        documentation = "The maximum refundable CTC for this person."
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            child_amount = max_(
                person("ctc_child_individual_maximum", period),
                person("ctc_child_individual_maximum_arpa", period),
            )
            # Use either normal or ARPA CTC maximums.
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            p = parameters(period).gov.contrib.ctc.additional_bracket.amount
            refundable_max = p.actc.calc(age) * is_dependent
            return tax_unit.sum(min_(child_amount, refundable_max))

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_child_individual_maximum)
            self.update_variable(ctc_refundable_maximum)

    return reform


def create_ctc_additional_bracket_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_additional_bracket()

    p = parameters.gov.contrib.ctc.additional_bracket

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_additional_bracket()
    else:
        return None


ctc_additional_bracket = create_ctc_additional_bracket_reform(
    None, None, bypass=True
)
