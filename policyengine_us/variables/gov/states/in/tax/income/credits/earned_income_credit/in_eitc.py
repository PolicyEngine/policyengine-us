from policyengine_us.model_api import *


class in_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21"
    defined_for = "in_eitc_eligible"

    def formula(tax_unit, period, parameters):
        # calculate eitc amount with federal formula except max of two children
        base_eitc = 
        p = parameters(period).gov.states["in"].tax.income
        return base_eitc * p.credits.earned_income.match_rate
