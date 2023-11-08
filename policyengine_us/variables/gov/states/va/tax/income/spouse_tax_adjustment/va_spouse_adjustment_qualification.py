from policyengine_us.model_api import *


class va_spouse_adjustment_qualification(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        person = tax_unit.members
        # Check whether the filer is eligible for age and blind exemptions

        # Consider using existed parameters here for addition and multiplication.

        personal_exemption_age_qualification = (
            person("age", period) >= p.age_threshold
        )
        personal_exemption_blind_qualification = person("is_blind", period)
        agi = person("va_agi", period)
        personal_va_agi = person(
            "va_prorate_fraction", period
        ) * person.tax_unit.sum(agi)

        total_personal_exemptions = (
            personal_exemption_age_qualification
            + personal_exemption_blind_qualification
        ) * p.age_blind_multiplier + p.addition_amount

        eligibility_requirement = personal_va_agi - total_personal_exemptions

        # replace this with 'is_tax_unit_head_or_spouse.py

        # If either amount is 0 or less, the filer does not qualify for this credit.
        return (
            tax_unit.min_(
                person("is_tax_unit_head_or_spouse", period)
                * eligibility_requirement
            )
            > 0
        )
