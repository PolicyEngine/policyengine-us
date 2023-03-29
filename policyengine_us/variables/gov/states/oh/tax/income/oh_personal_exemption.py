from policyengine_us.model_api import *


class oh_personal_exemption(Variable):
    value_type = bool
    entity = TaxUnit
    label = "OH personal exemption"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_dependent", period)
        is_tax_unit_head = tax_unit("is_tax_unit_head", period)
        is_spouse = person("is_spouse", period)
        num_of_dependents = tax_unit.sum(is_dependent)
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        personal_exemption_amount = parameters(
            period
        ).gov.states.oh.tax.income.personal_exemption_amount
        return (
            num_of_dependents + has_spouse + (is_tax_unit_head & ~is_dependent)
        ) * personal_exemption_amount
