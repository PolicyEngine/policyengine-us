from policyengine_us.model_api import *


class ga_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://houpl.org/wp-content/uploads/2023/01/2022-IT-511_Individual_Income_Tax_-Booklet-compressed.pdf#page=14"
        "https://www.zillionforms.com/2021/I2122607361.PDF#page14"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
