from openfisca_us.model_api import *


class il_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL personal exemption amount"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.il.tax.income.personal_exemption.personal_exemption

        filing_status = tax_unit("filing_status", period)
        joint = where(
            filing_status == filing_status.possible_values.JOINT,
            "joint",
            "nonjoint",
        )

        il_base_income = tax_unit("il_base_income", period)

        claimable_count = add(tax_unit, period, ["dsi_spouse", "dsi"])

        single_ineligible = (
            (joint == "nonjoint")
            & (claimable_count > 0)
            & (il_base_income > p["nonjoint"])
        )

        joint_ineligible = (
            (joint == "joint")
            & (claimable_count > 1)
            & (il_base_income > p["joint"])
        )

        joint_partner_ineligible = (
            (joint == "joint")
            & (claimable_count == 1)
            & (il_base_income > p["nonjoint"])
        )

        return where(
            single_ineligible | joint_ineligible,
            0,
            where(joint_partner_ineligible, p["nonjoint"], p[joint]),
        )
