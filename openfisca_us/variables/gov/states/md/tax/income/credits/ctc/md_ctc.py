from openfisca_us.model_api import *


class md_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD CTC"
    documentation = "Maryland Child Tax Credit"

    def formula(tax_unit, period, parameters):
        eligible = (
            tax_unit("adjusted_gross_income", period)
            <= parameters(
                period
            ).gov.states.md.tax.income.credits.ctc.eligibility.agi_cap
        )
        person = tax_unit.members
        is_dependent_and_disabled = (
            person("is_tax_unit_dependent", period)
            & person("is_disabled", period)
        ) & person("age", period) < 17
        eligible_dependents = tax_unit.sum(is_dependent_and_disabled)
        refund_per_dependent = parameters(
            period
        ).gov.states.md.tax.income.credits.ctc.refund_per_dependent

        return eligible * (eligible_dependents * refund_per_dependent)
