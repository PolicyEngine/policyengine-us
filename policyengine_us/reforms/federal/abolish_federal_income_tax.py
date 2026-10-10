from policyengine_us.model_api import *
from policyengine_us.reforms.federal.household_totals import exclude_from_total


def create_abolish_federal_income_tax() -> Reform:
    class reform(Reform):
        def apply(self):
            exclude_from_total(
                self,
                "household_tax_before_refundable_credits",
                "income_tax_before_refundable_credits",
            )
            exclude_from_total(
                self,
                "household_refundable_tax_credits",
                "income_tax_refundable_credits",
            )

    return reform


def create_abolish_federal_income_tax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_abolish_federal_income_tax()

    p = parameters(period).gov.contrib.ubi_center.flat_tax

    if p.abolish_federal_income_tax:
        return create_abolish_federal_income_tax()
    else:
        return None


abolish_federal_income_tax = create_abolish_federal_income_tax_reform(
    None, None, bypass=True
)
