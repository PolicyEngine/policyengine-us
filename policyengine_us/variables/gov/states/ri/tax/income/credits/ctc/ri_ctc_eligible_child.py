from policyengine_us.model_api import *


class ri_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Rhode Island Child Tax Credit eligible child"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#bookmark6"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.ctc
        age = person("age", period)
        return age <= p.age_limit
