from policyengine_us.model_api import *


class self_employed_health_insurance_ald_excluded_premiums(Variable):
    value_type = float
    entity = Person
    label = "Medical premiums excluded by a person's self-employed deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://pub.njleg.gov/bills/9899/PL99/222_.HTM",
    ]
    documentation = (
        "Medical premiums paid by a person and separately deducted through "
        "that person's self-employed health insurance ALD. Premium inputs "
        "use payer attribution, including family coverage paid by that "
        "person. The exclusion cannot consume another person's premiums."
    )

    def formula(person, period, parameters):
        premiums = person("medical_expense_health_insurance_premiums", period)
        deduction = person("self_employed_health_insurance_ald_person", period)
        return min_(premiums, max_(0, deduction))
