from policyengine_us.model_api import *


class ar_exemptions(Variable):
    value_type = float
    entity = Person
    label = "Arkansas exemptions from income tax for each individual"
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=10"
    defined_for = StateCode.AR
    unit = USD
    definition_period = YEAR
    adds = "gov.states.ar.tax.income.exemptions.exemptions"
