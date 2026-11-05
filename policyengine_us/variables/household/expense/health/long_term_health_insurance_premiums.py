from policyengine_us.model_api import *


class long_term_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Long-term health insurance premiums"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual long-term care insurance premiums paid for this person's own "
        "contract, excluding pretax payroll deductions and employer-paid "
        "premiums. Unlike the other premium inputs, which sit on the person "
        "who paid them, record these on the insured person, whoever in the "
        "tax unit paid them: 26 U.S.C. 213(d)(10) limits the premiums that "
        "count as medical care by the insured person's age. The model treats "
        "the insured person as the payer, so these premiums enter only that "
        "person's own self-employed health insurance deduction. Pretax payroll "
        "payments belong only in pre_tax_health_insurance_premiums. The "
        "pretax and non-pretax sets are disjoint; total person-paid premiums "
        "equal pretax payments plus the applicable non-pretax aggregate. This "
        "component must be counted only once when included in a broader "
        "premium input."
    )
    # No dataset fills this input, and CMS's health expenditure projections
    # have no long-term care insurance premium series. 26 U.S.C.
    # 213(d)(10)(B) indexes the deductible limits on these premiums by the
    # chained CPI-U medical care component for August of the preceding year.
    # CBO and CMS do not project that index, so this uses CBO's projection of
    # the CPI-U medical care component, by calendar year, as a proxy.
    uprating = "gov.bls.cpi.cpi_u_medical_care"
