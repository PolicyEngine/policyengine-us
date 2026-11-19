from policyengine_us.model_api import *


class me_fairness_credit_federal_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Maine fairness credit federal income with net losses added back"
    documentation = (
        "Federal total income with any net loss on a federal income line "
        "added back, Schedule PTFC/STFC line 2a plus line 2d. A loss first "
        "offsets other income on its own line (Form 1040 line 7, Schedule 1 "
        "lines 3, 5 and 6), so only the line's net loss is added back."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5213-A.html",  # 1. B. (1)
        "https://legislature.maine.gov/statutes/36/title36sec5219-KK.html",  # 1. D. (1)
        # PDF pages 1, 4: lines 2a and 2d, and the line 2d instructions
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=1",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        lines = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.federal_lines
        gross_income_sources = parameters(period).gov.irs.gross_income.sources
        person = tax_unit.members
        # A tax unit dependent's items are on the dependent's own return, as
        # in irs_gross_income.
        not_dependent = ~person("is_tax_unit_dependent", period)
        # irs_gross_income adds each filer's income from each source and
        # leaves out its losses: federal total income with every loss added
        # back.
        income = add(tax_unit, period, ["irs_gross_income"])
        # Line 2d adds back only a line's net loss, so a loss first offsets
        # the income on the same line, the head's and the spouse's together.
        # Schedule 1 line 4 (other_net_gain) is already a tax unit amount, and
        # the model has no losses on the other lines.
        for line in [
            lines.schedule_1_line_3,
            lines.schedule_1_line_5,
            lines.schedule_1_line_6,
            lines.form_1040_line_7,
        ]:
            line_income = 0
            line_losses = 0
            for source in line:
                # Only the sources federal gross income counts.
                if source in gross_income_sources:
                    amount = not_dependent * add(person, period, [source])
                    line_income += tax_unit.sum(max_(0, amount))
                    line_losses += tax_unit.sum(max_(0, -amount))
            income = income - min_(line_income, line_losses)
        return income
