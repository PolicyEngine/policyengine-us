from policyengine_us.model_api import *


class wi_homestead_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf",
        "https://www.revenue.wi.gov/TaxForms2023/2023-ScheduleH.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        income = add(tax_unit, period, p.homestead.income.sources)
        disqualified_losses = tax_unit("wi_homestead_disqualified_losses", period)
        # The $500 deduction is for each dependent under IRC 152; a return on
        # which the claimant (or, if joint, either spouse) can be claimed as a
        # dependent has none (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        return income + disqualified_losses - dependents * p.homestead.income.exemption
