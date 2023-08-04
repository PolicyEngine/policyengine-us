from policyengine_us.model_api import *


class oh_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Personal Exemption"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        total_exemptions = tax_unit("tax_unit_size", period)
        dependent_on_another_return = tax_unit("dsi", period)
        agi = tax_unit("oh_agi", period)
        p = parameters(period).gov.states.oh.tax.income.exemptions.personal
        credit_amount = p.amount.calc(agi)
        total_credit = total_exemptions * credit_amount
        return ~dependent_on_another_return * total_credit
