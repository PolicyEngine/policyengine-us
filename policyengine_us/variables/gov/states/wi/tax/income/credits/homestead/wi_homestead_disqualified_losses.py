from policyengine_us.model_api import *


class wi_homestead_disqualified_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit disqualified losses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52/1e",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52/6",
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
        person_losses = 0
        for source in p.disqualified_loss_sources:
            person_losses = person_losses + max_(0, -person(source, period))
        # Schedule 4, lines 5 and 6: a partnership loss is not netted against
        # S corporation income, or the reverse. The split losses are never
        # less than the net loss of partnership_s_corp_income, which is the
        # amount left when that aggregate is set directly with no split.
        partnership_loss = max_(0, -person("partnership_income", period))
        s_corp_loss = max_(0, -person("s_corp_income", period))
        net_pass_through_loss = max_(0, -person("partnership_s_corp_income", period))
        person_losses = person_losses + max_(
            partnership_loss + s_corp_loss, net_pass_through_loss
        )
        # Schedule 4, line 9: net loss from the sale of business property
        # (Form 4797), a tax-unit amount. other_net_gain does not separate
        # the losses from involuntary conversions that line 9 leaves out.
        business_property_loss = max_(0, -tax_unit("other_net_gain", period))
        # Schedule 4, line 3: net capital loss included in income.
        capital_loss = max_(0, -tax_unit("loss_limited_net_capital_gains", period))
        return (
            tax_unit.sum(person_losses * head_or_spouse)
            + business_property_loss
            + capital_loss
        )
