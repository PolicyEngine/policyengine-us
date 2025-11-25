from policyengine_us.model_api import *


class co_care_worker_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Care Worker Tax Credit eligible"
    defined_for = StateCode.CO
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-5/section-39-22-566/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.care_worker
        joint = tax_unit("tax_unit_is_joint", period)
        agi = tax_unit("adjusted_gross_income", period)
        income_limit = where(
            joint, p.income_limit.joint, p.income_limit.non_joint
        )
        income_eligible = agi <= income_limit
        eligible_care_worker_present = (
            tax_unit(
                "co_care_worker_credit_eligible_care_worker_count", period
            )
            > 0
        )
        return income_eligible & eligible_care_worker_present
