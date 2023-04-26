from policyengine_us.model_api import *


class oh_exemption_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio exemption credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        is_tax_unit_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        eligible_spouse = tax_unit.sum(is_spouse & ~is_dependent)
        eligible_head = tax_unit.sum(is_tax_unit_head & ~is_dependent)
        num_of_dependents = tax_unit("tax_unit_dependents", period)
        agi = tax_unit("oh_agi", period)
        num_of_exemptions = eligible_spouse + eligible_head + num_of_dependents

        p = parameters(period).gov.states.oh.tax.income
        personal_exemption_amount = (
            p.credits.exemption.personal_exemption_amount.calc(agi)
        )
        under_agi_less_exemption_cap = (
            agi - personal_exemption_amount * num_of_exemptions
        ) < p.credits.exemption.agi_less_exemption_cap
        credit_amount = p.credits.exemption.credit_amount
        return under_agi_less_exemption_cap * num_of_exemptions * credit_amount
