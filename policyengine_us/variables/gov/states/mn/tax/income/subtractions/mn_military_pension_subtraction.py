from policyengine_us.model_api import *


class mn_military_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota Military Pension Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.27",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1m-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Minnesota allows a full subtraction of military retirement pay
        # This includes:
        # - Service in active component (10 USC 1401-1414)
        # - Reserve component retirement (10 USC 12733)
        # - Survivor benefit plan payments (10 USC 1447-1455)
        military_pension = add(
            tax_unit,
            period,
            ["military_retirement_pay", "military_retirement_pay_survivors"],
        )
        return military_pension
