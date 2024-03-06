from policyengine_us.model_api import *


class mt_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Montana standard deduction when married couples are filing separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        p = parameters(period).gov.states.mt.tax.income.deductions.standard
        agi = person("mt_agi", period)
        # standard deduction is a percentage of AGI that
        # is bounded by a min/max by filing status.
        floor = p.floor[filing_status]
        cap = p.cap[filing_status]
        uncapped_amount = p.rate * agi
        deduction_amount = max_(min_(uncapped_amount, cap), floor)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * deduction_amount
