from policyengine_us.model_api import *


class la_oss(Variable):
    value_type = float
    entity = Person
    label = "Louisiana Optional State Supplement (OSS)"
    unit = USD
    definition_period = MONTH
    defined_for = "la_oss_eligible"
    reference = (
        "https://ldh.la.gov/assets/medicaid/MedicaidEligibilityPolicy/J-0000.pdf#page=2",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/la.html",
    )

    def formula(person, period, parameters):
        # OSS = personal care needs allowance (state standard) - federal SSI
        # institutional payment - countable income, floored at zero and capped
        # at the maximum payment.
        p = parameters(period).gov.states.la.hhs.oss
        federal_institutional = parameters(
            period
        ).gov.ssa.ssi.amount.institutional.individual
        countable_income = person("ssi_countable_income", period)
        raw = p.personal_care_needs_allowance - federal_institutional - countable_income
        return min_(max_(raw, 0), p.maximum_payment)
