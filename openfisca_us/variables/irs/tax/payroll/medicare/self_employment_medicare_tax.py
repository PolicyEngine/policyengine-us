from openfisca_us.model_api import *


class self_employment_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Self-employment health insurance payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        rate = parameters(period).irs.payroll.medicare.self_employment.rate
        base = max_(
            0, person("sey", period) * person.tax_unit("sey_frac", period)
        )
        return rate * base
