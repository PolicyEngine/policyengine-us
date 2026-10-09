from policyengine_us.model_api import *


class mn_military_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Military Pension Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.21",  # Subd. 21 - Military service pension; retirement pay
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=7",  # Line 25 instructions
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # The subtraction applies only to retirement pay included in federal
        # AGI, which excludes dependents' income; dependents report it on
        # their own return.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            ["military_retirement_pay", "military_retirement_pay_survivors"],
        )
