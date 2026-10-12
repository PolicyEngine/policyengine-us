from policyengine_us.model_api import *


class ca_wdp_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "California 250 Percent Working Disabled Program gross earned income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dhcs.ca.gov/services/working-disabled-program/"
    defined_for = StateCode.CA

    adds = "gov.ssa.ssi.income.sources.earned"
