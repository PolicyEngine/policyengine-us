from policyengine_us.model_api import *


class va_agi_less_exemptions_indv(Variable):
    value_type = float
    entity = TaxUnit
    label = "Difference between individual VAGI and personal exemptions"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_tax_adjustment
        # Check whether the filer is eligible for age and blind exemptions

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

        return (personal_va_agi - total_personal_exemptions) * person(
            "is_tax_unit_head_or_spouse", period
        )
