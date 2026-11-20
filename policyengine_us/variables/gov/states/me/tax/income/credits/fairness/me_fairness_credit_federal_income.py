from policyengine_us.model_api import *


class me_fairness_credit_federal_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine fairness credit federal income with losses added back"
    documentation = (
        "Federal gross income with losses added back. Trade or business, "
        "capital and farm losses are added back in full. The Schedule E items "
        "that make up Schedule 1 line 5 are combined first, so only their net "
        "loss is added back."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B. (1)
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D. (1)
        # PDF pages 1, 4: line 2d and its instructions, which add back a net
        # loss on Schedule 1 line 5
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=1",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.fairness
        gross_income_sources = parameters(period).gov.irs.gross_income.sources
        person = tax_unit.members
        # A tax unit dependent's items are on the dependent's own return, as
        # in irs_gross_income.
        not_dependent = ~person("is_tax_unit_dependent", period)
        # irs_gross_income adds each filer's income from each source and
        # leaves out its losses, so trade or business, capital and farm losses
        # are added back in full.
        income = add(tax_unit, period, ["irs_gross_income"])
        # Only "any net loss resulting from combining" the Schedule E items is
        # added back, so their losses first offset their income, the head's
        # and the spouse's together.
        schedule_e_income = 0
        schedule_e_losses = 0
        for source in p.federal_lines.schedule_1_line_5:
            # Only the sources federal gross income counts.
            if source in gross_income_sources:
                amount = not_dependent * add(person, period, [source])
                schedule_e_income = schedule_e_income + tax_unit.sum(max_(0, amount))
                schedule_e_losses = schedule_e_losses + tax_unit.sum(max_(0, -amount))
        return income - min_(schedule_e_income, schedule_e_losses)
