from policyengine_us.model_api import *


class income_driven_repayment_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Income-driven repayment adjusted gross income"
    unit = USD
    documentation = (
        "Adjusted gross income on the most recent federal income tax return "
        "available when the Department of Education sets the monthly payment. "
        "For the Repayment Assistance Plan, 20 U.S.C. 1087e(q)(4)(A) defines it "
        "as adjusted gross income 'for the most recent taxable year'. For the "
        "Income-Based Repayment, SAVE, Pay As You Earn and Income-Contingent "
        "Repayment plans, 34 CFR 685.209(b)(10)(i) defines income as adjusted "
        "gross income as reported to the IRS, which the Department takes from "
        "the latest return it obtains (685.209(l)(1)-(3); 20 U.S.C. "
        "1098e(c)(2)(A)(i)). Whose income counts follows 685.209(e)(1)(i), and "
        "(e)(1)(ii) for the Income-Contingent Repayment plan. A borrower whose "
        "income fell can document current income instead (685.209(l)(6)). "
        "When not provided, this defaults to the current year's adjusted gross "
        "income, because household inputs usually cover only the simulated "
        "year. The default overstates payments for borrowers whose income rose "
        "since their last return. An explicit input overrides it. Family size "
        "and the Repayment Assistance Plan's dependent count still come from "
        "the current year's inputs, so an override from an earlier return "
        "mixes years."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/20/1087e#q_4_A",
        "https://www.law.cornell.edu/uscode/text/20/1098e#c_2_A_i",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(b)(10)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(i)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(e)(1)(ii)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(l)(1)",
        "https://www.ecfr.gov/current/title-34/section-685.209#p-685.209(l)(6)",
    )
    adds = ["adjusted_gross_income"]
