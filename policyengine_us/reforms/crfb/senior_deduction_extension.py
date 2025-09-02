from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def senior_deduction_extension_reform() -> Reform:
    class taxable_income_deductions_if_itemizing(Variable):
        value_type = float
        entity = TaxUnit
        label = "Deductions if itemizing"
        unit = USD
        reference = "https://www.law.cornell.edu/uscode/text/26/63"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov
            year = period.start.year

            # Get the standard deductions list from the parameter
            deductions_list = list(p.irs.deductions.deductions_if_itemizing)

            # If we're past 2028 and senior deduction is not already in the list, add it
            if (
                year >= 2029
                and "additional_senior_deduction" not in deductions_list
            ):
                deductions_list.append("additional_senior_deduction")

            # Calculate total deductions
            return add(tax_unit, period, deductions_list)

    class taxable_income_deductions_if_not_itemizing(Variable):
        value_type = float
        entity = TaxUnit
        label = "Deductions if not itemizing"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov
            year = period.start.year

            # Get the standard deductions list from the parameter
            deductions_list = list(
                p.irs.deductions.deductions_if_not_itemizing
            )

            # If we're past 2028 and senior deduction is not already in the list, add it
            if (
                year >= 2029
                and "additional_senior_deduction" not in deductions_list
            ):
                deductions_list.append("additional_senior_deduction")

            # Calculate total deductions
            return add(tax_unit, period, deductions_list)

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_income_deductions_if_itemizing)
            self.update_variable(taxable_income_deductions_if_not_itemizing)

    return reform


def create_senior_deduction_extension_reform(
    parameters, period, bypass: bool = False
):
    # Create a create_{reform name} function that initializes the reform object
    # There are two sufficient conditions for this function to return
    # the reform

    # 1. If bypass is set to true
    if bypass is True:
        return senior_deduction_extension_reform()

    # 2. If boolean in extension.yaml is set to true
    parameter = parameters.gov.contrib.crfb.senior_deduction
    current_period = period_(period)
    reform_active = False

    for i in range(5):
        if parameter(current_period).extension:
            # If in any of the next five years, the boolean is true,
            # set the boolean reform_active to true, and stop the check,
            # i.e., assume the reform is active in all subsequent years.
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    # if the loop set reform_active to true, return the reform.
    if reform_active:
        return senior_deduction_extension_reform()
    else:
        return None


# Create a reform object to by setting bypass to true,
# for the purpose of running tests
senior_deduction_extension_reform_object = (
    create_senior_deduction_extension_reform(None, None, bypass=True)
)
