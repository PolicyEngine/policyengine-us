from openfisca_us.model_api import *

# TODO: Rename to something more specific, like


class EligibilityStatus(Enum):
    ELIGIBLE = 1
    PARTNER_INELIGIBLE = 2
    NOT_ELIGIBLE = 3


class il_personal_exemption_eligibility_status(Variable):
    value_type = Enum
    possible_values = EligibilityStatus
    default_value = EligibilityStatus.NOT_ELIGIBLE
    entity = TaxUnit
    label = (
        "Whether The Tax Unit Is Eligible For The Illinois Personal Exemption"
    )
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        personal_eligiblity_amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        # First, determine whether the tax unit is filing jointly or not.
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        tax_unit_personal_eligibility_amount = personal_eligiblity_amount * where(joint, 2, 1)

        # Then, determine whether either the head or the spouse of the tax unit is claimable as a dependent in another unit.
        claimable_count = add(tax_unit, period, ["dsi_spouse", "dsi"])
        il_base_income = tax_unit("il_base_income", period)

        # Criteria for complete ineligibility.
        ineligible = (
            (not joint)
            & (claimable_count > 0)
            & (
                il_base_income
                > tax_unit_personal_eligibility_amount
            )
        ) | (
            joint
            & (claimable_count > 1)
            & (
                il_base_income
                > tax_unit_personal_eligibility_amount
            )
        )

        # Criteria for partial ineligibility.
        partner_ineligible = (
            joint
            & (claimable_count == 1)
            & (
                il_base_income
                > tax_unit_personal_eligibility_amount
            )
        )

        # Based on the criteria, return the eligibility status.
        return select(
            [ineligible, partner_ineligible],
            [
                EligibilityStatus.NOT_ELIGIBLE,
                EligibilityStatus.PARTNER_INELIGIBLE,
            ],
            EligibilityStatus.ELIGIBLE,
        )
