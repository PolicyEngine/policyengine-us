from policyengine_us.model_api import *


class pa_nontaxable_roth_conversions(Variable):
    value_type = float
    entity = Person
    label = "Roth conversions taxable by US but not by PA"
    unit = USD
    documentation = "US taxable Roth conversions excluded from PA AGI."
    definition_period = YEAR
    reference = "https://revenue-pa.custhelp.com/app/answers/detail/a_id/274/~/taxability-of-roth-iras-according-to-pa-income-tax-rules"
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        return person("taxable_roth_conversions", period)
