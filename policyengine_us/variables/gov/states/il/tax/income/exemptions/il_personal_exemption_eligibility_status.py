from policyengine_us.model_api import *


class ILPersonalExemptionEligibilityStatus(Enum):
    BOTH_ELIGIBLE = 1
    PARTIALLY_ELIGIBLE = 2
    NOT_ELIGIBLE = 3


class il_personal_exemption_eligibility_status(Variable):
    value_type = Enum
    possible_values = ILPersonalExemptionEligibilityStatus
    default_value = ILPersonalExemptionEligibilityStatus.NOT_ELIGIBLE
    entity = TaxUnit
    label = (
        "Whether The Tax Unit Is Eligible For The Illinois Personal Exemption"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        personal_eligibility_amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        # First, determine whether the tax unit is filing jointly or not
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        tax_unit_personal_eligibility_amount = (
            personal_eligibility_amount * where(joint, 2, 1)
        )

        # Then, determine whether either the head or the spouse of the
        # tax unit is claimable as a dependent in another unit
        claimable_count = add(
            tax_unit,
            period,
            ["head_is_dependent_elsewhere", "spouse_is_dependent_elsewhere"],
        )
        il_base_income = tax_unit("il_base_income", period)

        # Criteria for complete ineligibility
        ineligible = (
            (
                ~joint
                & (claimable_count > 0)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (
                joint
                & (claimable_count > 1)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (
                joint
                & (claimable_count == 2)
                & (il_base_income > tax_unit_personal_eligibility_amount * 2)
            )
        )

        # Criteria for partial ineligibility
        partner_ineligible = (
            (
                joint
                & (claimable_count == 1)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (~joint & (claimable_count == 0))
            | (
                ~joint
                & (claimable_count == 1)
                & (il_base_income < tax_unit_personal_eligibility_amount)
            )
        )

        # Based on the criteria, return the eligibility status
        return select(
            [ineligible, partner_ineligible],
            [
                ILPersonalExemptionEligibilityStatus.NOT_ELIGIBLE,
                ILPersonalExemptionEligibilityStatus.PARTIALLY_ELIGIBLE,
            ],
            ILPersonalExemptionEligibilityStatus.BOTH_ELIGIBLE,
        )
