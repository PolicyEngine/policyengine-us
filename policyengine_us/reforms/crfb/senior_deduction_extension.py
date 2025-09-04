from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_senior_deduction_extension() -> Reform:
    def modify_parameters(parameters):
        # Update deductions_if_itemizing to include additional_senior_deduction after 2028
        parameters.gov.irs.deductions.deductions_if_itemizing.update(
            start=instant("2029-01-01"),
            stop=instant("2099-12-31"),
            value=[
                "qualified_business_income_deduction",
                "wagering_losses_deduction",
                "itemized_taxable_income_deductions",
                "additional_senior_deduction",
            ],
        )

        # Update deductions_if_not_itemizing to include additional_senior_deduction after 2028
        parameters.gov.irs.deductions.deductions_if_not_itemizing.update(
            start=instant("2029-01-01"),
            stop=instant("2099-12-31"),
            value=[
                "standard_deduction",
                "qualified_business_income_deduction",
                "additional_senior_deduction",
                "charitable_deduction_for_non_itemizers",
            ],
        )

        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_senior_deduction_extension_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_senior_deduction_extension()

    p = parameters.gov.contrib.crfb.senior_deduction_extension

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).applies:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_senior_deduction_extension()
    else:
        return None


senior_deduction_extension = create_senior_deduction_extension_reform(
    None, None, bypass=True
)
