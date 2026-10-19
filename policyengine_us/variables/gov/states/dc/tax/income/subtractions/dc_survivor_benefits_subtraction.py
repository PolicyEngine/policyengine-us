from policyengine_us.model_api import *


class dc_survivor_benefits_subtraction(Variable):
    value_type = float
    entity = Person
    label = "DC government survivor benefits subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.02#a_2_N_ii",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2024_D40_Booklet_011525.pdf#page=34",
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.subtractions.survivor_benefits
        # Dependents' income is not in federal AGI; they report it on their
        # own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        eligible = (age >= p.min_age) & head_or_spouse
        # D.C. Code § 47-1803.02(a)(2)(N)(ii) allows exclusion of survivor benefits
        # received from the District or federal government by persons 62 or older.
        survivor_pay = person("military_retirement_pay_survivors", period)
        return eligible * survivor_pay
