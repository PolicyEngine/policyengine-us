from policyengine_us.model_api import *


class or_erdc_copay(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = USD
    label = "Oregon ERDC monthly copay"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0050"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].delc.erdc
        income = spm_unit("or_erdc_countable_income", period)
        size = clip(
            spm_unit("spm_unit_size", period.this_year),
            2,
            p.max_group_size,
        )
        amount = select(
            [
                size == 2,
                size == 3,
                size == 4,
                size == 5,
                size == 6,
                size == 7,
                size == 8,
            ],
            [
                p.copay.size_2.calc(income),
                p.copay.size_3.calc(income),
                p.copay.size_4.calc(income),
                p.copay.size_5.calc(income),
                p.copay.size_6.calc(income),
                p.copay.size_7.calc(income),
                p.copay.size_8.calc(income),
            ],
            default=p.copay.size_8.calc(income),
        )
        # OAR 414-175-0023(3)(d)-(f) also waives the copay after a permanent
        # job loss, a military transition, or medical leave at application;
        # these circumstances are not tracked at the moment.
        categorical = spm_unit("or_erdc_categorically_eligible", period)
        return where(categorical, 0, amount)
