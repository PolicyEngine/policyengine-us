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
        reference = "https://punchbowl.news/smitmo_017_xml/"  # page 35

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.reconciliation.additional_sd_reduction
            aged_count = add(
                tax_unit,
                period,
                [
                    "meets_additional_senior_standard_deduction_identification_requirements"
                ],
            )
            base_deduction = p.amount * aged_count
            agi = tax_unit("adjusted_gross_income", period)
            p = parameters(
                period
            ).gov.contrib.reconciliation.additional_sd_reduction
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            phase_out_amount = where(
                joint, p.rate.joint.calc(agi), p.rate.other.calc(agi)
            )
            return max_(base_deduction - phase_out_amount, 0)

    class eligible_senior_for_additional_senior_standard_deduction(Variable):
        value_type = bool
        entity = Person
        label = "Eligible senior for additional senior standard deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://punchbowl.news/smitmo_017_xml/"  # page 35

        def formula(person, period, parameters):
            p = parameters(period).gov.irs.deductions.standard.aged_or_blind
            age = person("age", period)
            aged = age >= p.age_threshold
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            meets_identification_requirements = person(
                "meets_additional_sd_identification_requirements", period
            )
            return aged & head_or_spouse & meets_identification_requirements

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

    def modify_parameters(parameters):
        parameters.gov.irs.deductions.deductions_if_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "charitable_deduction",
                "interest_deduction",
                "salt_deduction",
                "medical_expense_deduction",
                "casualty_loss_deduction",
                "qualified_business_income_deduction",
                "wagering_losses_deduction",
                "tuition_and_fees_deduction",
                "misc_deduction",
                "additional_senior_standard_deduction",
            ],
        )
        parameters.gov.irs.deductions.deductions_if_not_itemizing.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "charitable_deduction_for_non_itemizers",
                "standard_deduction",
                "qualified_business_income_deduction",
                "additional_senior_standard_deduction",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(
                meets_additional_senior_standard_deduction_identification_requirements
            )
            self.update_variable(
                eligible_senior_for_additional_senior_standard_deduction
            )
            self.update_variable(additional_senior_standard_deduction)
            self.modify_parameters(modify_parameters)

    return reform


def create_reconciled_additional_senior_standard_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_additional_senior_standard_deduction()

    p = parameters.gov.contrib.reconciliation.additional_sd_reduction

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
