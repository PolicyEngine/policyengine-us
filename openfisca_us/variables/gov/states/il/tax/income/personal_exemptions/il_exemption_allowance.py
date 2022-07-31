from openfisca_us.model_api import *


class il_exemption_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.personal_exemption

        personal_exemption_amount = p.personal_exemption_allowance

        filing_status = tax_unit("filing_status", period)
        filing_statuses = tax_unit("filing_status", period).possible_values
        joint = filing_status == filing_statuses.JOINT

        il_base_income = tax_unit("il_base_income", period)

        claimable_count = add(tax_unit, period, ["dsi_spouse", "dsi"])

        aged_blind_count = tax_unit("aged_blind_count", period)
        aged_blind_exemption = aged_blind_count * p.senior_and_blind_exemption

        dependent_exemption = personal_exemption_amount * tax_unit(
            "tax_unit_dependents", period
        )

        il_is_exemption_eligible = where(
            joint,
            tax_unit("adjusted_gross_income", period) < 500000,
            tax_unit("adjusted_gross_income", period) < 250000,
        )

        base_exemption_allowance = where(
            joint,
            where(
                claimable_count > 0,
                where(
                    il_base_income
                    < claimable_count * personal_exemption_amount,
                    personal_exemption_amount * 2,
                    personal_exemption_amount * (claimable_count - 1),
                ),
                personal_exemption_amount * 2,
            ),
            where(
                claimable_count > 0,
                where(
                    il_base_income < personal_exemption_amount,
                    personal_exemption_amount,
                    0,
                ),
                personal_exemption_amount,
            ),
        )

        total_amount = (
            base_exemption_allowance
            + aged_blind_exemption
            + dependent_exemption
        )

        return where(il_is_exemption_eligible, total_amount, 0)
