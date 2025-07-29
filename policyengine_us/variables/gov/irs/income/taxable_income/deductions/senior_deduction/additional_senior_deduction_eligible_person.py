from policyengine_us.model_api import *


class additional_senior_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person is eligible for the additional senior deduction"
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text"
    )

    def formula(person, period, parameters):
        ssn_card_type = person("ssn_card_type", period)
        ssn_card_str = ssn_card_type.decode_to_str()
        p = parameters(period).gov.irs.deductions.senior_deduction
        eligible_ssn_card_type = np.isin(
            ssn_card_str, p.eligible_ssn_card_type
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        p_irs = parameters(period).gov.irs.deductions.standard.aged_or_blind
        aged = age >= p_irs.age_threshold
        return eligible_ssn_card_type & head_or_spouse & aged
