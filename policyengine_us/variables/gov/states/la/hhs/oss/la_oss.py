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
        # Per SSA 2011 LA report: state supplement = state standard - federal
        # SSI payment - countable income. The federal payment is the actual
        # `ssi` (post-reduction for institutional residents), not the constant
        # institutional FBR — using the constant under-pays people with
        # low-but-positive countable income still receiving partial SSI, and
        # also under-pays non-SSI recipients in LTC. J-300's $1.00 floor and
        # $0.50/$0.49 round-up rule are not modeled at the moment.
        p = parameters(period).gov.states.la.hhs.oss
        ssi = person("ssi", period)
        countable_income = person("ssi_countable_income", period)
        raw = p.personal_care_needs_allowance - ssi - countable_income
        return min_(max_(raw, 0), p.maximum_payment)
