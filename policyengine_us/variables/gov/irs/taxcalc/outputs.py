from policyengine_us.model_api import *


class filer_earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit_non_dep_sum("earned", tax_unit, period))


class earned(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Earned income"
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(person, period, parameters):
        misc = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - misc.self_emp_tax_adj)
            * misc.employer_share
            * person("self_employment_tax", period)
        )
        return person("earned_income", period) - adjustment
