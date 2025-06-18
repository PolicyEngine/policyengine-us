from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
import numpy as np


def create_tax_on_agi() -> Reform:
    class tax_on_agi(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "Tax on AGI"

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.tax_on_agi
            if p.in_effect:
                tax_unit = person.tax_unit
                adjusted_gross_income = tax_unit("adjusted_gross_income", period)
                filing_status = tax_unit("filing_status", period)

                filing_statuses = filing_status.possible_values
                return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.SURVIVING_SPOUSE,
            ],
             [
                p.rates.single.calc(adjusted_gross_income),
                p.rates.joint.calc(adjusted_gross_income),
                p.rates.separate.calc(adjusted_gross_income),
                p.rates.head_of_household.calc(adjusted_gross_income),
                p.rates.surviving_spouse.calc(adjusted_gross_income),
            ],
            )
            return 0
        
    class household_net_income(Variable):
        value_type = float
        entity = Household
        label = "net income"
        definition_period = YEAR
        unit = USD
        adds = [
            "household_market_income",
            "household_benefits",
            "household_refundable_tax_credits",
        ]
        subtracts = ["household_tax_before_refundable_credits", "tax_on_agi"]

    class reform(Reform):
        def apply(self):
            self.update_variable(tax_on_agi)
            self.update_variable(household_net_income)
    return reform


def create_tax_on_agi_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_tax_on_agi()

    p = (
        parameters.gov.contrib.tax_on_agi
    )

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_tax_on_agi()
    else:
        return None

tax_on_agi = (
    create_tax_on_agi_reform(
        None, None, bypass=True
    )
)
