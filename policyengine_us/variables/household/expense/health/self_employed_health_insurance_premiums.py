from policyengine_us.model_api import *


class self_employed_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance premiums"
    unit = USD
    documentation = (
        "The model takes Form 7206 line 1 premiums from the non-pretax "
        "health_insurance_premiums input. It excludes pretax payroll "
        "deductions and employer-paid premiums, except eligible payments or "
        "reimbursements from the person's own partnership or S corporation "
        "in which they own more than 2% (Notice 2008-1). Enter those "
        "payments in health_insurance_premiums, without recording them as "
        "employer contributions of SOME or ALL. Pretax payroll payments "
        "belong only in pre_tax_health_insurance_premiums; the pretax and "
        "non-pretax sets remain disjoint. The model excludes premiums when "
        "self_employed_health_insurance_employer_plan_eligible holds. That "
        "variable documents the annual coverage assumptions and the "
        "own-business coverage flags that still trigger the model's bar. "
        "Congress disallows a deduction for the part of Marketplace "
        "premiums the premium tax credit pays under 26 U.S.C. 280C(g). "
        "The model takes premiums as supplied and does not net the credit "
        "it calculates out of them. Calculating the credit depends on AGI "
        "and this deduction (policyengine-us #10124)."
    )
    definition_period = YEAR
    defined_for = "is_self_employed"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l",
        "https://www.irs.gov/pub/irs-prior/f7206--2025.pdf#page=1",  # Line 1
        # PDF pages 3-4
        "https://www.irs.gov/pub/irs-drop/n-08-01.pdf#page=3",
    )

    def formula(person, period, parameters):
        premiums = person("health_insurance_premiums", period)
        employer_plan_eligible = person(
            "self_employed_health_insurance_employer_plan_eligible", period
        )
        return where(employer_plan_eligible, 0, premiums)
