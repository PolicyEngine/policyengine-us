from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_additional_senior_standard_deduction() -> Reform:
    class additional_senior_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Additional senior standard deduction"
        unit = USD
        definition_period = YEAR
        defined_for = "filer_meets_additional_senior_standard_deduction_identification_requirements"
        reference = "https://punchbowl.news/smitmo_017_xml/"  # page 35

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.additional_senior_standard_deduction
            aged_head = tax_unit("aged_head", period).astype(int)
            aged_spouse = tax_unit("aged_spouse", period).astype(int)
            aged_count = aged_spouse + aged_head
            base_deduction = p.amount * aged_count
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            phase_out_amount = where(
                joint, p.rate.joint.calc(agi), p.rate.other.calc(agi)
            )
            return max_(base_deduction - phase_out_amount, 0)

    class filer_meets_additional_senior_standard_deduction_identification_requirements(
        Variable
    ):
        value_type = bool
        entity = TaxUnit
        definition_period = YEAR
        label = "Filer meets additional senior standard deduction identification requirements"

        def formula(tax_unit, period, parameters):
            # Both head and spouse in the tax unit must have valid SSN card type to be eligible for the CTC
            person = tax_unit.members
            is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            eligible_ssn_card_type = person(
                "meets_additional_senior_standard_deduction_identification_requirements",
                period,
            )
            ineligible_head_or_spouse = (
                is_head_or_spouse & ~eligible_ssn_card_type
            )
            return tax_unit.sum(ineligible_head_or_spouse) == 0

    class meets_additional_senior_standard_deduction_identification_requirements(
        Variable
    ):
        value_type = bool
        entity = Person
        definition_period = YEAR
        label = "Person meets additional standard deduction identification requirements"
        reference = "https://punchbowl.news/smitmo_017_xml/"  # page 35

        def formula(person, period, parameters):
            ssn_card_type = person("ssn_card_type", period)
            ssn_card_types = ssn_card_type.possible_values
            citizen = ssn_card_type == ssn_card_types.CITIZEN
            non_citizen_valid_ead = (
                ssn_card_type == ssn_card_types.NON_CITIZEN_VALID_EAD
            )
            return citizen | non_citizen_valid_ead

    class taxable_income_deductions_if_itemizing(Variable):
        value_type = float
        entity = TaxUnit
        label = "Deductions if itemizing"
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/63"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.deductions
            existing_deductions = add(
                tax_unit, period, p.deductions_if_itemizing
            )
            additional_deduction = tax_unit(
                "additional_senior_standard_deduction", period
            )
            return existing_deductions + additional_deduction

    class taxable_income_deductions_if_not_itemizing(Variable):
        value_type = float
        entity = TaxUnit
        label = "Deductions if not itemizing"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.deductions
            existing_deductions = add(
                tax_unit, period, p.deductions_if_not_itemizing
            )
            additional_deduction = tax_unit(
                "additional_senior_standard_deduction", period
            )
            return existing_deductions + additional_deduction

    class reform(Reform):
        def apply(self):
            self.update_variable(
                meets_additional_senior_standard_deduction_identification_requirements
            )
            self.update_variable(
                filer_meets_additional_senior_standard_deduction_identification_requirements
            )
            self.update_variable(additional_senior_standard_deduction)
            self.update_variable(taxable_income_deductions_if_not_itemizing)
            self.update_variable(taxable_income_deductions_if_itemizing)

    return reform


def create_reconciled_additional_senior_standard_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_additional_senior_standard_deduction()

    p = (
        parameters.gov.contrib.reconciliation.additional_senior_standard_deduction
    )

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_additional_senior_standard_deduction()
    else:
        return None


reconciled_additional_senior_standard_deduction = (
    create_reconciled_additional_senior_standard_deduction_reform(
        None, None, bypass=True
    )
)
