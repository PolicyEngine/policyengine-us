from openfisca_us.model_api import *


class ecpa_adult_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "End Child Poverty Act Adult Dependent Credit"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).contrib.congress.tlaib.end_child_poverty_act.adult_dependent_credit
        # Adult dependent credit.
        dependent = person("is_tax_unit_dependent", period)
        adult = person("age", period) >= p.min_age
        return p.amount * tax_unit.sum(adult & dependent)
