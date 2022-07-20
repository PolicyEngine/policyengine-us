# Parameters: amount ($1,000 - verify), phase_out.start ($25,000), phase_out.increment ($100), phase_out.amount ($20), max_age (5)
# Variables: tax/income/credits/earned_income/ca_is_eligible_for_caleitc.py - NO FORMULA
# Formula: Involves parameters and ca_is_eligible_for_caleitc variable
# Tests: ca_is_eligible_for_caleitc as input (along with earned_income, etc.)
# Stepped phase out example:
# https://github.com/PolicyEngine/openfisca-us/blob/master/openfisca_us/variables/gov/irs/credits/cdcc/cdcc_rate.py

from openfisca_us.model_api import *


class ca_young_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA young child tax credit"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.ftb.ca.gov/forms/2021/2021-3514.pdf#page=3")

    def formula(tax_unit, period, parameters, ca_is_eligible_for_caleitc):
        p = parameters(period).gov.states.ca.tax.income.credits.young_child
        agi = tax_unit("adjusted_gross_income", period)

        # check if eligible
        has_eligible_child = False
        in_ca = tax_unit.household("state_code_str", period) == "CA"
        eligible = ca_is_eligible_for_caleitc & in_ca & has_eligible_child

        # First phase-out
        excess_agi = max_(0, agi - p.phase_out.start)
        increments = excess_agi / p.phase_out.increment
        reduction = increments * p.phase_out.amount
        return eligible * np.rint(p.amount -  reduction)
        

        

        