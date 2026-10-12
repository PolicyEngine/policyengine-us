from policyengine_us.model_api import *


class ok_ccs_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Oklahoma Child Care Subsidy family share copayment"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4.pdf#page=2",
        "https://okrules.elaws.us/oac/340:40-5-1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.copay
        # The monthly family share copayment is read from the Appendix C-4
        # schedule by adjusted monthly income and family size. Households
        # larger than the largest published size (10) use the size-10 column.
        income = spm_unit("ok_ccs_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        copay = select(
            [size == n for n in range(1, 10)],
            [getattr(p.amount, f"size_{n}").calc(income) for n in range(1, 10)],
            default=p.amount.size_10.calc(income),
        )
        # Predetermined eligible households (public assistance or SSI
        # recipients) have no family share copayment (OAC 340:40-7-1(b)(1)).
        predetermined = spm_unit("ok_ccs_predetermined_eligible", period)
        return where(predetermined, 0, copay)
