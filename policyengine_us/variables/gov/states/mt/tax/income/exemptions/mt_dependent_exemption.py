from policyengine_us.model_api import *


class mt_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana dependent exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        person = tax_unit.members
        is_disabled = person("is_disabled", period)
        employment_income = person("employment_income", period)
        healthy_qualified_dependent = (
            person("is_tax_unit_dependent", period)
            & (employment_income <= p.amount)
            & (is_disabled == False)
        )
        disabled_qualified_dependent = (
            person("is_tax_unit_dependent", period)
            & (employment_income <= p.amount)
            & (is_disabled == True)
        )

        num_healthy_dependent = tax_unit.sum(healthy_qualified_dependent)
        num_disabled_dependent = tax_unit.sum(disabled_qualified_dependent)

        return (num_healthy_dependent + 2 * num_disabled_dependent) * p.amount
