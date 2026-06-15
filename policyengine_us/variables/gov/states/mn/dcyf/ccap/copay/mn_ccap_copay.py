from policyengine_us.model_api import *


class mn_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP family copayment"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # DHS-6413N copayment schedules; Minn. Stat. 142E.15.
        "https://edocs.dhs.state.mn.us/lfserver/Public/DHS-6413N-ENG#page=6",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.copay.biweekly
        annual_income = spm_unit("mn_ccap_countable_income", period.this_year)
        # Copayment schedules are published by household size from 2 through 13.
        # Households with 13 or more people use the 13-person column.
        size = spm_unit("spm_unit_size", period.this_year)
        biweekly_copay = select(
            [
                size <= 2,
                size == 3,
                size == 4,
                size == 5,
                size == 6,
                size == 7,
                size == 8,
                size == 9,
                size == 10,
                size == 11,
                size == 12,
            ],
            [
                p.size_2.calc(annual_income),
                p.size_3.calc(annual_income),
                p.size_4.calc(annual_income),
                p.size_5.calc(annual_income),
                p.size_6.calc(annual_income),
                p.size_7.calc(annual_income),
                p.size_8.calc(annual_income),
                p.size_9.calc(annual_income),
                p.size_10.calc(annual_income),
                p.size_11.calc(annual_income),
                p.size_12.calc(annual_income),
            ],
            default=p.size_13.calc(annual_income),
        )
        # Convert the biweekly copayment to a monthly amount (26 pay periods
        # per year over 12 months).
        return biweekly_copay * 26 / MONTHS_IN_YEAR
