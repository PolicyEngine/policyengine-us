from policyengine_us.model_api import *


class nc_military_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina military retirement deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "nc_military_retirement_deduction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nc.tax.income.deductions.military_retirement
        military_retirement_benefits = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        return military_retirement_benefits * p.fraction
