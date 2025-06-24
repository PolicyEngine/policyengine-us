from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ctc_ssn() -> Reform:
    class ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Child Tax Credit"
        unit = USD
        documentation = "Total value of the non-refundable and refundable portions of the Child Tax Credit."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#a"
        defined_for = "filer_meets_ctc_identification_requirements"

        def formula(tax_unit, period, parameters):
            maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
            reduction = tax_unit("ctc_phase_out", period)
            return max_(0, maximum_amount - reduction)

    class filer_meets_ctc_identification_requirements(Variable):
        value_type = bool
        entity = TaxUnit
        definition_period = YEAR
        label = "Filer meets CTC identification requirements"

        def formula(tax_unit, period, parameters):
            # Both head and spouse in the tax unit must have valid SSN card type to be eligible for the CTC
            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            eligible_ssn_card_type = person(
                "meets_ctc_identification_requirements", period
            )
            p = parameters(period).gov.contrib.reconciliation.ctc
            if p.one_person_ssn_req:
                return tax_unit.any(head_or_spouse & eligible_ssn_card_type)
            return ~tax_unit.any(head_or_spouse & ~eligible_ssn_card_type)

    class meets_ctc_identification_requirements(Variable):
        value_type = bool
        entity = Person
        definition_period = YEAR
        label = "Person meets CTC identification requirements"
        reference = "https://docs.house.gov/meetings/WM/WM00/20250513/118260/BILLS-119CommitteePrintih.pdf#page=4"

        def formula(person, period, parameters):
            ssn_card_type = person("ssn_card_type", period)
            ssn_card_types = ssn_card_type.possible_values
            citizen = ssn_card_type == ssn_card_types.CITIZEN
            non_citizen_valid_ead = (
                ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
            )
            return citizen | non_citizen_valid_ead

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc)
            self.update_variable(filer_meets_ctc_identification_requirements)
            self.update_variable(meets_ctc_identification_requirements)

    return reform


def create_ctc_ssn_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ctc_ssn()

    p = parameters.gov.contrib.reconciliation.ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_ssn()
    else:
        return None


ctc_ssn = create_ctc_ssn_reform(None, None, bypass=True)
