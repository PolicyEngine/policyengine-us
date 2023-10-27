from policyengine_us.model_api import *


class va_spouse_adjustment_qualification(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        person = tax_unit.members
        # Check whether the filer is eligible for age and blind exemptions
        personal_exemption_age_qualification = (
            person("age", period) >= p.age_threshold
        )
        personal_exemption_blind_qualification = person("is_blind", period)

        # Todo: create a personal 'vagi' variable?
        personal_vagi = person("vagi", period)

        total_personal_exemptions = (
            personal_exemption_age_qualification
            + personal_exemption_blind_qualification
        ) * p.age_blind_multiplier + p.addition_amount
        meets_requirement = personal_vagi - total_personal_exemptions > 0

        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse

        # If either amount is 0 or less, the filer does not qualifify for this credit.
        return tax_unit.min_(head_or_spouse * meets_requirement) > 0
