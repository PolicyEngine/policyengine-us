from policyengine_us.model_api import *
from policyengine_us.reforms.federal.household_totals import exclude_from_total


def create_abolish_payroll_tax() -> Reform:
    class reform(Reform):
        def apply(self):
            exclude_from_total(
                self,
                "household_tax_before_refundable_credits",
                "employee_payroll_tax",
            )

    return reform


def create_abolish_payroll_tax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_abolish_payroll_tax()

    p = parameters(period).gov.contrib.ubi_center.flat_tax

    if p.abolish_payroll_tax:
        return create_abolish_payroll_tax()
    else:
        return None


abolish_payroll_tax = create_abolish_payroll_tax_reform(None, None, bypass=True)
