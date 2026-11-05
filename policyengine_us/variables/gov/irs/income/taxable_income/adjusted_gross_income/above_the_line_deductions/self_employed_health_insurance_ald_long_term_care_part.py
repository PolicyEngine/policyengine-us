from policyengine_us.model_api import *


class self_employed_health_insurance_ald_long_term_care_part(Variable):
    value_type = float
    entity = Person
    label = "Long-term care part of a person's self-employed health insurance deduction"
    unit = USD
    documentation = (
        "The part of a person's self-employed health insurance deduction "
        "(self_employed_health_insurance_ald_person) that took eligible "
        "long-term care premiums (Form 7206 line 2): the deduction left after "
        "the person's medical insurance premiums (line 1), limited to the "
        "person's line 2 premiums. The rest of the deduction took no "
        "long-term care premiums, so a supplied person deduction above lines "
        "1 and 2 adds nothing here."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_C",
        "https://www.irs.gov/pub/irs-prior/f7206--2024.pdf#page=1",  # Lines 1-3
    )

    def formula(person, period, parameters):
        deduction = max_(0, person("self_employed_health_insurance_ald_person", period))
        medical_part = min_(
            person("self_employed_health_insurance_premiums", period), deduction
        )
        return min_(
            person("self_employed_long_term_care_premiums", period),
            deduction - medical_part,
        )
