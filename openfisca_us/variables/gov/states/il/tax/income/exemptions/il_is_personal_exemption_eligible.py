from openfisca_us.model_api import *


class EligibilityStatus(Enum):
    ELIGIBLE = 1
    PARTNER_INELIGIBLE = 2
    NOT_ELIGIBLE = 3


class il_is_personal_exemption_eligible(Variable):
    value_type = Enum
    possible_values = EligibilityStatus
    default_value = EligibilityStatus.NOT_ELIGIBLE
    entity = TaxUnit
    label = "Whether The Tax Unit Is Eligible For The Illinois Personal Exemption"
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        personal_eligiblity_amounts = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        filing_status = tax_unit("filing_status", period)
        joint = (filing_status == filing_status.possible_values.JOINT)
        claimable_count = add(tax_unit, period, ["dsi_spouse", "dsi"])
        il_base_income = tax_unit("il_base_income", period)

        ineligible = (
            (not joint)
            & (claimable_count > 0)
            & (
                il_base_income
                > personal_eligiblity_amounts[
                    EligibilityStatus.PARTNER_INELIGIBLE
                ]
            )
        ) | (
            joint
            & (claimable_count > 1)
            & (
                il_base_income
                > personal_eligiblity_amounts[EligibilityStatus.ELIGIBLE]
            )
        )

        partner_ineligible = (
            joint
            & (claimable_count == 1)
            & (
                il_base_income
                > personal_eligiblity_amounts[
                    EligibilityStatus.PARTNER_INELIGIBLE
                ]
            )
        )

        return select(
            [ineligible, partner_ineligible],
            [
                EligibilityStatus.NOT_ELIGIBLE,
                EligibilityStatus.PARTNER_INELIGIBLE,
            ],
            EligibilityStatus.ELIGIBLE,
        )
