from policyengine_us.model_api import *


class ar_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=22"
    defined_for = StateCode.AR
