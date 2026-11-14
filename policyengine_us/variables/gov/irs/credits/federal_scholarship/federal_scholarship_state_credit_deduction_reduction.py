from policyengine_us.model_api import *


class federal_scholarship_state_credit_deduction_reduction(Variable):
    value_type = float
    entity = Person
    label = "Scholarship state credit reduction of charitable contributions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Actual section 1.170A-1(h)(3) reduction attributable to the qualified "
        "slice. The default treats the donor's qualified cash as one payment or "
        "homogeneous payments and uses the allowed state credit as the expected "
        "maximum. Supply this value explicitly for mixed receipts/payments, "
        "different expected versus allowed state credits, or payment-specific "
        "15-percent exceptions. This adjustment does not award a state credit."
    )
    reference = (
        "https://www.ecfr.gov/current/title-26/section-1.170A-1#p-1.170A-1(h)(3)"
    )

    def formula_2027_01_01(person, period, parameters):
        p = parameters(period).gov.irs.credits.federal_scholarship
        qualified = person(
            "federal_scholarship_qualified_contributions_eligible", period
        )
        state_credit = max_(person("federal_scholarship_state_tax_credit", period), 0)
        exception = qualified * p.state_credit_deduction_exception_rate
        return where(state_credit > exception, min_(state_credit, qualified), 0)
