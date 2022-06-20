from openfisca_us.model_api import *


class total_disability_payments(Variable):
    value_type = float
    entity = Person
    label = "Disability (total) payments"
    unit = USD
    documentation = "Wages (or payments in lieu thereof) paid to an individual for permanent and total disability"
    definition_period = YEAR


class section_22_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Section 22 income"
    unit = USD
    documentation = (
        "Income upon which the elderly or disabled credit is applied"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/22"

    def formula(tax_unit, period, parameters):
        elderly_disabled = parameters(
            period
        ).gov.irs.credits.elderly_or_disabled
        # Calculate initial amount
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        num_qualifying_individuals = tax_unit.sum(
            person("qualifies_for_elderly_or_disabled_credit", period)
        )
        initial_amount = select(
            [
                num_qualifying_individuals == 1,
                num_qualifying_individuals == 2,
                filing_status == filing_status.possible_values.SEPARATE,
                True,
            ],
            [
                elderly_disabled.amount.one_qualified,
                elderly_disabled.amount.two_qualified,
                elderly_disabled.amount.separate,
                0,
            ],
        )

        # Limitations on under-65s

        is_elderly = person("age", period) >= elderly_disabled.age
        is_dependent = person("is_tax_unit_dependent", period)
        num_elderly = tax_unit.sum(is_elderly & ~is_dependent)
        disability_income = person("total_disability_payments", period)
        non_elderly_disability_income = tax_unit.sum(
            disability_income * ~is_elderly
        )

        cap = (
            num_elderly * elderly_disabled.amount.one_qualified
            + non_elderly_disability_income
        )

        capped_amount = min_(initial_amount, cap)
        total_pensions = add(tax_unit, period, ["pension_income"])
        taxable_pensions = add(tax_unit, period, ["taxable_pension_income"])
        non_taxable_pensions = total_pensions - taxable_pensions
        total_social_security = tax_unit("tax_unit_social_security", period)
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        non_taxable_social_security = (
            total_social_security - taxable_social_security
        )
        capped_reduced_amount = (
            capped_amount - non_taxable_pensions - non_taxable_social_security
        )
        agi = tax_unit("adjusted_gross_income", period)

        amount_over_phase_out = max_(
            0, agi - elderly_disabled.phase_out.threshold[filing_status]
        )
        phase_out_reduction = (
            elderly_disabled.phase_out.rate * amount_over_phase_out
        )

        return max_(0, capped_reduced_amount - phase_out_reduction)
