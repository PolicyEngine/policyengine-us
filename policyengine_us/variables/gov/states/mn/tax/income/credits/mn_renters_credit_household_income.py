from policyengine_us.model_api import *


class mn_renters_credit_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit household income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income
        minimum_age = p.credits.renters.age_threshold
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        household_agi = tax_unit.spm_unit("mn_renters_credit_household_agi", period) + (
            tax_unit("spouse_separate_adjusted_gross_income", period) * separate
        )
        exemption_amount = p.exemptions.amount

        people = tax_unit.members
        claimant = people("is_tax_unit_head_or_spouse", period)
        is_age_eligible = people("age", period) >= minimum_age
        is_disabled = people("is_permanently_and_totally_disabled", period)
        age_or_disability_subtraction = (
            tax_unit.any(claimant & (is_age_eligible | is_disabled)) * exemption_amount
        )

        dependent_count = tax_unit("tax_unit_dependents", period)
        dependent_subtraction_multiplier = (
            p.credits.renters.dependent_subtraction_multiplier.calc(dependent_count)
        )
        dependent_subtraction = exemption_amount * dependent_subtraction_multiplier

        subtractions = age_or_disability_subtraction + dependent_subtraction
        return max_(0, household_agi - subtractions)
