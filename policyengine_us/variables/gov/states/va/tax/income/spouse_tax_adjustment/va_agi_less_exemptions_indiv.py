from policyengine_us.model_api import *


class va_agi_less_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Difference between individual VAGI and personal exemption amounts"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        # Step 1: take person level AGI from head and sposue
        agi = person("va_agi_individual", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_or_spouse_agi = agi * head_or_spouse
        # Step 2: Check whether the filer is eligible for age and blind exemptions
        # and compute the value
        # age -
        p = parameters(period).gov.states.va.tax.income.exemptions
        # Check whether the filer is eligible for age and blind exemptions
        personal_exemption_age_eligible = (
            person("age", period) >= p.spouse_tax_adjustment.age_threshold
        ).astype(int)
        personal_exemption_blind_eligible = person("is_blind", period).astype(
            int
        )
        aged_blind_amount = p.aged_blind * (
            personal_exemption_blind_eligible + personal_exemption_age_eligible
        )

        total_personal_exemptions = (
            aged_blind_amount + p.personal
        ) * head_or_spouse
        # Step 3: subtract the Exemption amount from the AGI for each head and spouse
        # tax form allows the amount to be less than 0
        return head_or_spouse_agi - total_personal_exemptions
