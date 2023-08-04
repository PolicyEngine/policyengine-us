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
        dependent = person("is_tax_unit_dependent", period)
        # To qualify for an exemption, the dependent must either:
        # a) have gross income below the exemption amount, or
        # b) be a qualifying child under IRC 152(c), which defines for the EITC
        gross_income = person("irs_gross_income", period)
        meets_income_test = gross_income <= p.amount
        qualifying_child = person("is_eitc_qualifying_child", period)
        eligible = dependent & (meets_income_test | qualifying_child)
        # Disabled dependents get an additional exemption.
        exemptions_if_eligible = p.disabled + person("is_disabled", period)
        dependent_exemptions = tax_unit.sum(eligible * exemptions_if_eligible)
        return dependent_exemptions * p.amount
