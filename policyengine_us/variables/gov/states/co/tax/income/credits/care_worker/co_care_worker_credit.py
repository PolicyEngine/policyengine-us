from policyengine_us.model_api import *


class co_care_worker_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Care Worker Tax Credit"
    defined_for = "co_care_worker_credit_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/colorado/title-39/specific-taxes/income-tax/article-22/part-5/section-39-22-566/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.care_worker
        joint = tax_unit("tax_unit_is_joint", period)
        eligible_care_worker_count = tax_unit(
            "co_care_worker_credit_eligible_care_worker_count", period
        )
        joint_with_two_eligible_care_workers = joint & (
            eligible_care_worker_count == 2
        )
        return where(
            joint_with_two_eligible_care_workers,
            p.amount.joint,
            p.amount.non_joint,
        )
