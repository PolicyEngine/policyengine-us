from policyengine_us.model_api import *


class ms_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = (
        "Mississippi standard deduction when married couples file separately"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.ms.tax.income.deductions.standard
        return is_head_or_spouse * p.amount[filing_status]
