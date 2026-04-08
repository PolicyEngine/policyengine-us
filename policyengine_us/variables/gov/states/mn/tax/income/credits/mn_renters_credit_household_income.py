from policyengine_us.model_api import *


DEPENDENT_SUBTRACTION_MULTIPLIERS = np.array([0.0, 1.4, 2.7, 3.9, 5.0, 6.0])


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
        mn_agi = (
            tax_unit("adjusted_gross_income", period)
            + tax_unit("mn_additions", period)
            - tax_unit("mn_subtractions", period)
        )
        spouse_agi = tax_unit("mn_renters_credit_spouse_agi", period)
        nonresident_income = tax_unit("mn_renters_credit_nonresident_income", period)
        exemption_amount = p.exemptions.amount

        people = tax_unit.members
        claimant = people("is_tax_unit_head_or_spouse", period)
        is_age_eligible = people("age", period) >= 65
        is_disabled = people("is_permanently_and_totally_disabled", period)
        age_or_disability_subtraction = tax_unit.any(
            claimant & (is_age_eligible | is_disabled)
        ) * exemption_amount

        dependent_count = tax_unit("tax_unit_dependents", period)
        capped_dependent_count = min_(dependent_count, 5).astype(int)
        dependent_subtraction = exemption_amount * DEPENDENT_SUBTRACTION_MULTIPLIERS[
            capped_dependent_count
        ]

        seiu_subtraction = tax_unit(
            "mn_renters_credit_seiu_stipend_subtraction", period
        )
        subtractions = (
            nonresident_income
            + age_or_disability_subtraction
            + dependent_subtraction
            + seiu_subtraction
        )
        return max_(0, mn_agi + spouse_agi - subtractions)

