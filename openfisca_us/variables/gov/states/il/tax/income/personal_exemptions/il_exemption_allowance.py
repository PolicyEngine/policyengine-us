from openfisca_us.model_api import *


class il_exemption_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.exemptions
            period
        ).gov.states.il.tax.income.personal_exemption.amount
        senior_and_blind_exemption_amount = parameters(
            period
        ).gov.states.il.tax.income.personal_exemption.senior_and_blind_exemption

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint = filing_status == filing_statuses.JOINT

        il_base_income = tax_unit("il_base_income", period)

        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        claimable = person("il_tax_unit_claimable", period)

        claimable_count = sum(claimable & (head | spouse))
        aged_blind_count = tax_unit("aged_blind_count", period)
        aged_blind_exemption = aged_blind_count * p.aged_blind
            [tax_unit("aged_head", period), tax_unit("aged_spouse", period)]
        )
        blind_count = sum(
            [tax_unit("blind_head", period), tax_unit("blind_spouse", period)]
        )

        senior_exemption = senior_and_blind_exemption_amount * senior_count
        blind_exemption = senior_and_blind_exemption_amount * blind_count
        dependent_exemption = personal_exemption_amount * tax_unit(
            "tax_unit_dependents", period
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
            + senior_exemption
            + blind_exemption
            + dependent_exemption
        )

        return where(
            joint,
            where(
                tax_unit("adjusted_gross_income", period) > 500000,
                0,
                total_amount,
            ),
            where(
                tax_unit("adjusted_gross_income", period) > 250000,
                0,
                total_amount,
            ),
        )
