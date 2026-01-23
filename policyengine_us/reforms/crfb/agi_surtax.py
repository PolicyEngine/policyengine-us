from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def agi_surtax_reform() -> Reform:
    class agi_surtax(Variable):
        value_type = float
        entity = TaxUnit
        label = "AGI surtax"
        definition_period = YEAR
        unit = USD

        def formula(tax_unit, period, parameters):
            agi = tax_unit("adjusted_gross_income", period)
            p = parameters(period).gov.contrib.crfb.surtax
            if p.increased_base.in_effect:
                additional_sources = add(
                    tax_unit, period, p.increased_base.sources
                )
                agi += additional_sources
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            return where(
                joint, p.rate.joint.calc(agi), p.rate.single.calc(agi)
            )

    class income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Income tax before credits"
        definition_period = YEAR
        unit = USD

        adds = [
            "income_tax_main_rates",
            "capital_gains_tax",
            "alternative_minimum_tax",
            "agi_surtax",
        ]

    class reform(Reform):
        def apply(self):
            self.update_variable(agi_surtax)
            self.update_variable(income_tax_before_credits)

    return reform


def create_agi_surtax_reform(parameters, period, bypass: bool = False):
    # Create a create_{reform name} function that initializes the reform object
    # There are two sufficient conditions for this function to return
    # the reform

    # 1. If bypass is set to true
    if bypass is True:
        return agi_surtax_reform()

    # 2. If boolean in in_effect.yaml is set to true
    parameter = parameters.gov.contrib.crfb.surtax
    current_period = period_(period)
    reform_active = False

    for i in range(5):
        if parameter(current_period).in_effect:
            # If in any of the next five years, the boolean is true,
            # set the boolean reform_active to true, and stop the check,
            # i.e., assume the reform is active in all subsequent years.
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    # if the loop set reform_active to true, return the reform.
    if reform_active:
        return agi_surtax_reform()
    else:
        return None


# Create a reform object to by setting bypass to true,
# for the purpose of running tests
agi_surtax_reform_object = create_agi_surtax_reform(None, None, bypass=True)
