from policyengine_us.model_api import *


class ms_self_employment_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi adjustemnts to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        self_employment = add(tax_unit, period, ["self_employment_tax"])
        p = parameters(
            period
        ).gov.states.ms.tax.income.subtractions.self_employment
        return self_employment * p.rate
