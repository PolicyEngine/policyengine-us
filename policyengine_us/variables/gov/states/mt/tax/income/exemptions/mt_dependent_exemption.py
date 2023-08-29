from policyengine_us.model_api import *


class mt_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana dependent exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/"
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
        total_eligible = tax_unit.sum(eligible)
        # Disabled dependents get an additional exemption.
        disabled = where(
            eligible, person("is_disabled", period).astype(int), 0
        )
        total_disabled = tax_unit.sum(disabled)
        dependent_exemptions = total_eligible + total_disabled
        return dependent_exemptions * p.amount
