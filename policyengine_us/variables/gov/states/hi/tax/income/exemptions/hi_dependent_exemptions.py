from policyengine_us.model_api import *


class hi_dependent_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii regular exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # The tax unit can claim exemptions for each dependent
        dependents = tax_unit("tax_unit_dependents", period)
        # The the head or the spouse is disabled, the dependent exemption goes to 0
        disabled_head = tax_unit("head_disabled", period)
        disabled_spouse = tax_unit("spouse_disabled", period)
        head_or_spouse_disabled = disabled_head | disabled_spouse
        base_amount = p.base * dependents
        return where(head_or_spouse_disabled, base_amount, 0)
