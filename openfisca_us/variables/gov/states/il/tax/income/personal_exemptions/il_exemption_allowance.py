from openfisca_us.model_api import *


class il_exemption_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        personal_exemption_amount = parameters(
            period
        ).gov.states.il.tax.personal_exemption.amount
        senior_and_blind_exemption_amount = parameters(
            period
        ).gov.states.il.tax.personal_exemption.senior_and_blind_exemption

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint = filing_status == filing_statuses.JOINT

        il_base_income = tax_unit("il_base_income", period)

        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        over_65 = person("age", period) > 65
        is_blind = person("is_blind", period)
        spouse = person("is_tax_unit_spouse", period)
        claimable = person("il_tax_unit_claimable", period)

        number_of_dependents = tax_unit("tax_unit_dependents", period)

        claimable_count = sum(claimable & (head | spouse))
        senior_count = sum(over_65 & (head | spouse))
        blind_count = sum(is_blind & (head | spouse))

        senior_exemption = senior_and_blind_exemption_amount * senior_count
        blind_exemption = senior_and_blind_exemption_amount * blind_count
        dependent_exemption = personal_exemption_amount * number_of_dependents

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

        return (
            base_exemption_allowance
            + senior_exemption
            + blind_exemption
            + dependent_exemption
        )
