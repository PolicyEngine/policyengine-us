from policyengine_us.model_api import *


class ga_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download#page=15",
        "https://www.zillionforms.com/2021/I2122607361.PDF#page14",
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ga.tax.income.subtractions
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
