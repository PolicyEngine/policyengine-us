from policyengine_us.model_api import *


class wi_homestead_disqualified_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit disqualified losses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2023/2023-ScheduleH.pdf#page=4",
        "https://www.revenue.wi.gov/TaxForms2023/2023-ScheduleH-inst.pdf#page=16",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Schedule H, Schedule 4: losses included in income are added back
        # to household income (line 11j). Each source is treated as one
        # activity, since PolicyEngine does not split income by business.
        p = parameters(period).gov.states.wi.tax.income.credits.homestead.income
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        person_losses = sum(
            max_(0, -person(source, period)) for source in p.disqualified_loss_sources
        )
        # Schedule 4, line 3: net capital loss included in income.
        capital_loss = max_(0, -tax_unit("loss_limited_net_capital_gains", period))
        return tax_unit.sum(person_losses * head_or_spouse) + capital_loss
