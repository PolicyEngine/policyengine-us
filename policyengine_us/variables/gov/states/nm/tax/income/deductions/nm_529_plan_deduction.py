from policyengine_us.model_api import *


class nm_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico 529 plan contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://hed.nm.gov/financial-aid/new-mexico-529-college-savings-plan",
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        return tax_unit("investment_in_529_plan", period)
