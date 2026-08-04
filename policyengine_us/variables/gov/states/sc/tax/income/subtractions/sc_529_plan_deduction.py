from policyengine_us.model_api import *


class sc_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina 529 plan contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.scstatehouse.gov/code/t59c002.php",
        "https://treasurer.sc.gov/about-us/newsroom/529-updates-in-one-big-beautiful-bill-give-south-carolina-families-even-more-flexibility-for-educational-savings/",
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        return tax_unit("investment_in_529_plan", period)
