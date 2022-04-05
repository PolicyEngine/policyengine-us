from openfisca_us.model_api import *


class payroll_taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return max_(
            0.0,
            person("sey", period) * person.tax_unit("sey_frac", period),
        )
