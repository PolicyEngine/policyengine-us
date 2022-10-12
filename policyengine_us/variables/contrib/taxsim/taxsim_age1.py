from policyengine_us.model_api import *


class taxsim_age1(Variable):
    value_type = int
    entity = TaxUnit
    label = "Age of first dependent"
    unit = "year"
    documentation = """Age of first dependent. Used for EITC, CTC and CCC. For 1991+ code students between 20 and 23 as 19 to get the EITC calculation correct. Code infants as "1". [For compatibiity with taxsim32, dep13-dep18 are accepted and have priority over age1-age3]. If niether dep19 or age1 are present in an uploaded file than depx is used for the number of child eligible for the EIC, CTC and CDCC."""
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        dependent_rank = person.get_rank(tax_unit, age, is_dependent)
        is_first_dependent = dependent_rank == 0
        return tax_unit.sum(age * is_first_dependent)
