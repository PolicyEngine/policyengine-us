from policyengine_us.model_api import *


class ri_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Rhode Island Child Tax Credit eligible child"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#:~:text=%E2%80%9CChild%E2%80%9D%20means%20an%20individual%20who%20is%20eighteen%20years%20of%20age%20or%20under"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.ctc
        age = person("age", period)
        return age <= p.age_limit
