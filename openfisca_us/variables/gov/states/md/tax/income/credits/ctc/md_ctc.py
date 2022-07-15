from openfisca_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CTC"
    definition_period = YEAR
    unit = USD
    documentation = "Maryland Child Tax Credit"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.tax.income.credits.ctc
        income_eligible = (
            tax_unit("adjusted_gross_income", period)
            <= parameters(period).gov.states.md.tax.income.credits.ctc.agi_cap
        )
        person = tax_unit.members
        eligible_child = (
            person("is_tax_unit_dependent", period)
            & person("is_disabled", period)
            * (person("age", period) < 17)
        )
        eligible_children = tax_unit.sum(eligible_child)
        return income_eligible * eligible_children * p.amount
            period
        ).gov.states.md.tax.income.credits.ctc.refund_per_child

        return eligible * (eligible_dependents * refund_per_child)
