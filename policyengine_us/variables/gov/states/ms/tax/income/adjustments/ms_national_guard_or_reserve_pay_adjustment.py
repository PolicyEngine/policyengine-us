from policyengine_us.model_api import *


class ms_national_guard_or_reserve_pay_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi national guard or reserve pay adjustment"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=12",
        "https://law.justia.com/codes/mississippi/2020/title-27/chapter-7/article-1/section-27-7-18/",  # 4(m)
    ]
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        military_income = add(tax_unit, period, ["military_service_income"])
        p = parameters(
            period
        ).gov.states.ms.tax.income.adjustments.national_guard_or_reserve_pay
        return min_(military_income, p.cap)
