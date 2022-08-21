from openfisca_us.model_api import *


class EligibilityStatus(Enum):
    ELIGIBLE = 1
    PARTNER_INELIGIBLE = 2
    NOT_ELIGIBLE = 3


# TODO: actually finish this variable


class il_is_exemption_eligible(Variable):
    value_type = Enum
    possible_values = EligibilityStatus
    entity = TaxUnit
    label = "Whether this tax unit is eligible for any exemptions"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.exemption.personal

        filing_status = tax_unit("filing_status", period)
        joint = (filing_status == filing_status.possible_values.JOINT,)
        claimable_count = add(tax_unit, period, ["dsi_spouse", "dsi"])
        il_base_income = tax_unit("il_base_income", period)

        ineligible = (
            (not joint)
            & (claimable_count > 0)
            & (il_base_income > p["nonjoint"])
        ) | (joint & (claimable_count > 1) & (il_base_income > p["joint"]))

        partner_ineligible = (
            joint & (claimable_count == 1) & (il_base_income > p["nonjoint"])
        )

        return select(
            [ineligible, partner_ineligible],
            [
                EligibilityStatus.NOT_ELIGIBLE,
                EligibilityStatus.PARTNER_INELIGIBLE,
            ],
            EligibilityStatus.ELIGIBLE,
        )
