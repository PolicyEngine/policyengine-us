from policyengine_us.model_api import *


class fl_oss(Variable):
    value_type = float
    entity = Person
    label = "Florida Optional State Supplementation"
    unit = USD
    definition_period = MONTH
    defined_for = "fl_oss_eligible"
    reference = (
        "https://www.flrules.org/gateway/RuleNo.asp?title=PUBLIC%20ASSISTANCE&ID=65A-2.036",
        "https://www.myflfamilies.com/sites/default/files/2025-05/Appendix%20A-12%20-%20State%20Funded%20Programs%20Eligibility%20Standards.pdf",
        "https://ffic.myflfamilies.com/manual/2600.pdf",
    )
    documentation = """
    Optional State Supplementation payment.

    This implements the DCF ESS Program Policy Manual 2640.0131.04 single-
    individual computation, expressed in the algebraically equivalent
    "recognized cost of care + personal needs allowance - countable income"
    form:

      2640.0131.04 Step 1: available income = gross income - PNA
      2640.0131.04 Step 2: deficit = recognized cost of care - available income
                         = cost of care - (income - PNA)
                         = (cost of care + PNA) - income

    Here fl_oss_provider_rate is the recognized standard for cost of care (the
    provider rate in Appendix A-12) and p.pna is the personal needs allowance,
    so total_needs = provider_rate + PNA and the payment is total_needs -
    ssi_countable_income, floored at $0 and capped by the Appendix A-12 Maximum
    OSS Payment (fl_oss_max_oss). The benefit is paid "in dollars and cents"
    (2640.0131.03); it is not rounded.

    Scope limitations relative to the manual (documented, not modeled):
      - 2640.0131.02/.05 dependent allocation: when an OSS individual has a
        non-institutionalized ineligible spouse/child in the community, a
        portion of income above the PNA is diverted to the dependent's need
        ($146 spouse, $65 per child), which raises the OSS payment. The
        person-level snapshot does not represent an OSS resident with a
        separate community-dependent unit and that unit's income, so this
        allocation is not applied. Its omission is conservative (it can only
        increase the payment).
      - 2640.0131.03 month-of-placement proration: PE computes full-month
        benefits; partial-month placement proration is not represented.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.oss
        # Recognized standard for cost of care (2640.0131.04); the provider rate
        # in Appendix A-12.
        provider_rate = person("fl_oss_provider_rate", period)
        # total_needs = recognized cost of care + personal needs allowance.
        total_needs = provider_rate + p.pna
        countable_income = person("ssi_countable_income", period)
        max_oss = person("fl_oss_max_oss", period)
        # Deficit (2640.0131.04 Step 2), floored at $0 and capped by the
        # Appendix A-12 Maximum OSS Payment.
        return min_(max_(total_needs - countable_income, 0), max_oss)
