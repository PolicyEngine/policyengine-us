from policyengine_us.model_api import *


class ny_mctmt_employer_tax(Variable):
    value_type = float
    entity = Person
    label = "New York Metropolitan Commuter Transportation Mobility Tax"
    documentation = (
        "Employer-side New York MCTMT liability attributable to this worker, "
        "using household county as a proxy for work location and employer "
        "quarterly payroll expense as a proxy for applicable zone brackets."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    reference = "https://www.tax.ny.gov/bus/mctmt/emp.htm"

    def formula(person, period, parameters):
        quarter_payroll = person("ny_mctmt_employer_quarterly_payroll_expense", period)
        in_zone_1 = person.household("in_nyc", period)
        in_zone_2 = person.household("in_ny_mctd_zone_2", period)
        p = parameters(period).gov.local.ny.mctd.tax.payroll

        applicable_rate = select(
            [in_zone_1, in_zone_2],
            [
                p.rates.zone_1.calc(quarter_payroll, right=True),
                p.rates.zone_2.calc(quarter_payroll, right=True),
            ],
            default=0,
        )

        return applicable_rate * person("payroll_tax_gross_wages", period)
