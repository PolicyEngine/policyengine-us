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
    label = "Whether The Tax Unit Is Eligible For The Illinois Personal Exemption"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://ilga.gov/documents/legislation/publicacts/103/PDF/103-0009.pdf#page=357"

    def formula(tax_unit, period, parameters):
        personal_eligibility_amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.personal

        # First, determine whether the tax unit is filing jointly or not
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        tax_unit_personal_eligibility_amount = personal_eligibility_amount * where(
            joint, 2, 1
        )

        # Count actual dependent claims among the head and spouse, as required
        # by 35 ILCS 5/204(b).
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        claimed_elsewhere = person("claimed_as_dependent_on_another_return", period)
        claimed_count = tax_unit.sum(head_or_spouse & claimed_elsewhere)
        il_base_income = tax_unit("il_base_income", period)

        # Criteria for complete ineligibility
        ineligible = (
            (
                ~joint
                & (claimed_count > 0)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (
                joint
                & (claimed_count > 1)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (
                joint
                & (claimed_count == 2)
                & (il_base_income > tax_unit_personal_eligibility_amount * 2)
            )
        )

        # Criteria for partial ineligibility
        partner_ineligible = (
            (
                joint
                & (claimed_count == 1)
                & (il_base_income > tax_unit_personal_eligibility_amount)
            )
            | (~joint & (claimed_count == 0))
            | (
                ~joint
                & (claimed_count == 1)
                & (il_base_income <= tax_unit_personal_eligibility_amount)
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
