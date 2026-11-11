from policyengine_us.model_api import *


class SelfEmployedHealthInsurancePlanBusiness(Enum):
    SCHEDULE_C = "Schedule C business"
    SCHEDULE_F = "Schedule F farm"
    PARTNERSHIP = "Partnership"
    S_CORPORATION = "S corporation"
    UNSPECIFIED = "Unspecified"


class self_employed_health_insurance_plan_business(Variable):
    value_type = Enum
    entity = Person
    possible_values = SelfEmployedHealthInsurancePlanBusiness
    default_value = SelfEmployedHealthInsurancePlanBusiness.UNSPECIFIED
    definition_period = YEAR
    label = (
        "Business under which the self-employed health insurance plan is established"
    )
    documentation = (
        "The trade or business under which the person's health insurance plan "
        "is established, or considered to be established: the Schedule C "
        "business, the Schedule F farm, a partnership in which the person has "
        "Schedule K-1 box 14 code A net earnings, or an S corporation in which "
        "the person is a more-than-2% shareholder. The self-employed health "
        "insurance deduction is limited to the earned income from that "
        "business alone (one Form 7206 per plan). Each kind of business is one "
        "total per person, because the inputs do not separate one business of "
        "a kind from another: the Schedule C business is all of the person's "
        "Schedule C income, SSTB and non-SSTB together, the farm all of their "
        "Schedule F profit, the partnership all of their K-1 box 14 code A "
        "earnings, and the S corporation all of their wages as a "
        "more-than-2% shareholder. A partner's or shareholder's own policy "
        "counts as established under the partnership or S corporation only "
        "when that business pays or reimburses the premiums and reports them "
        "as guaranteed payments or wages; enter those premiums in "
        "health_insurance_premiums. A partner also includes those guaranteed "
        "payments in partnership_income, and in "
        "partnership_self_employment_net_earnings when the partnership "
        "reports them in K-1 box 14 code A; a shareholder includes the wages "
        "in employment_income (see s_corp_shareholder_medicare_wages). "
        "Long-term care premiums the business pays "
        "or reimburses and reports the same way go in "
        "long_term_health_insurance_premiums, on the insured person. The "
        "deduction counts premiums only when "
        "is_self_employed is true, including for a shareholder whose only "
        "earned income is S corporation wages. UNSPECIFIED (the default) means the "
        "business was not supplied, and the limit uses the person's business "
        "with the largest earned income; name the business when a partnership "
        "or S corporation with the largest earned income does not pay or "
        "reimburse the premiums, or when the plan is established under a "
        "business other than the one with the largest earned income."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_A",
        # PDF pages 1-2
        "https://www.irs.gov/pub/irs-prior/i7206--2023.pdf#page=1",
        # Notice 2008-1: when a plan is established by the S corporation
        "https://www.irs.gov/pub/irs-drop/n-08-01.pdf#page=3",
        # Guaranteed payments to partners are net earnings from self-employment
        "https://www.irs.gov/pub/irs-prior/i1065--2023.pdf#page=43",
    )
