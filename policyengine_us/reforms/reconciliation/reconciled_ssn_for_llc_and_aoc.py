from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_reconciled_ssn_for_llc_and_aoc() -> Reform:
    # Amend the variables themselves, as the *_eligible flags indicate
    # the ability of individuals to count their educational expenses.
    # These reforms set identification requirements at the filer level.
    class lifetime_learning_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Lifetime Learning Credit"
        unit = USD
        documentation = "Value of the non-refundable Lifetime Learning Credit"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"
        defined_for = "filer_meets_llc_and_aoc_identification_requirements"

        def formula(tax_unit, period, parameters):
            education = parameters(period).gov.irs.credits.education
            llc = education.lifetime_learning_credit
            person = tax_unit.members
            is_aoc_eligible = person(
                "is_eligible_for_american_opportunity_credit", period
            )
            eligible_expenses = tax_unit.sum(
                person("qualified_tuition_expenses", period) * ~is_aoc_eligible
            )
            capped_expenses = min_(llc.expense_limit, eligible_expenses)
            maximum_amount = llc.rate * capped_expenses
            phase_out = tax_unit("education_credit_phase_out", period)
            if llc.abolition:
                return 0
            return max_(0, maximum_amount * (1 - phase_out))

    class american_opportunity_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "American Opportunity Credit"
        unit = USD
        documentation = "Total value of the American Opportunity Credit"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/25A#b"
        defined_for = "filer_meets_llc_and_aoc_identification_requirements"

        def formula(tax_unit, period, parameters):
            education = parameters(period).gov.irs.credits.education
            aoc = education.american_opportunity_credit
            person = tax_unit.members
            is_eligible = person(
                "is_eligible_for_american_opportunity_credit", period
            )
            tuition_expenses = (
                person("qualified_tuition_expenses", period) * is_eligible
            )
            maximum_amount_per_student = aoc.amount.calc(tuition_expenses)
            maximum_amount = tax_unit.sum(maximum_amount_per_student)
            phase_out = tax_unit("education_credit_phase_out", period)
            if aoc.abolition:
                return 0
            return max_(0, maximum_amount * (1 - phase_out))

    class filer_meets_llc_and_aoc_identification_requirements(Variable):
        value_type = bool
        entity = TaxUnit
        definition_period = YEAR
        label = "Filer meets LLC and AOC identification requirements"

        def formula(tax_unit, period, parameters):
            # Both head and spouse in the tax unit must have valid SSN card type to be eligible for the CTC
            person = tax_unit.members
            is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            eligible_ssn_card_type = person(
                "meets_llc_and_aoc_identification_requirements", period
            )
            ineligible_head_or_spouse = (
                is_head_or_spouse & ~eligible_ssn_card_type
            )
            return tax_unit.sum(ineligible_head_or_spouse) == 0

    class meets_llc_and_aoc_identification_requirements(Variable):
        value_type = bool
        entity = Person
        definition_period = YEAR
        label = "Person meets LLC and AOC identification requirements"
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
            self.update_variable(lifetime_learning_credit)
            self.update_variable(american_opportunity_credit)
            self.update_variable(
                filer_meets_llc_and_aoc_identification_requirements
            )
            self.update_variable(meets_llc_and_aoc_identification_requirements)

    return reform


def create_reconciled_ssn_for_llc_and_aoc_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciled_ssn_for_llc_and_aoc()

    p = parameters.gov.contrib.reconciliation.ssn_for_llc_and_aoc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciled_ssn_for_llc_and_aoc()
    else:
        return None


reconciled_ssn_for_llc_and_aoc = create_reconciled_ssn_for_llc_and_aoc_reform(
    None, None, bypass=True
)
