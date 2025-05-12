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
        defined_for = "tax_unit_has_valid_ssn_card_type_for_ctc"

        def formula(tax_unit, period, parameters):
            maximum_amount = tax_unit("ctc_maximum_with_arpa_addition", period)
            reduction = tax_unit("ctc_phase_out", period)
            return max_(0, maximum_amount - reduction)

    class tax_unit_has_valid_ssn_card_type_for_ctc(Variable):
        value_type = bool
        entity = TaxUnit
        definition_period = YEAR
        label = "All members in the tax unit have valid SSN card type to be eligible for the CTC"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_E"

        def formula(tax_unit, period, parameters):
            ssn_card_type = tax_unit.members("ssn_card_type", period)
            ssn_card_types = ssn_card_type.possible_values
            citizen = ssn_card_type == ssn_card_types.CITIZEN
            non_citizen_valid_ead = (
                ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
            )
            eligible_ssn_card_type = citizen | non_citizen_valid_ead
            return tax_unit.all(eligible_ssn_card_type)

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc)
            self.update_variable(tax_unit_has_valid_ssn_card_type_for_ctc)

    return reform


def create_ctc_ssn_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ctc_ssn()

    p = parameters.gov.contrib.reconciliation.ctc_ssn

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
