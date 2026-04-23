from policyengine_us.model_api import *


class ny_mctmt_total_employer_tax(Variable):
    value_type = float
    entity = Person
    label = "Total New York Metropolitan Commuter Transportation Mobility Tax"
    documentation = (
        "Employer-level New York MCTMT liability from aggregate quarterly "
        "payroll expense inputs in Zone 1 and Zone 2."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.tax.ny.gov/bus/mctmt/emp.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ny.mctd.tax.payroll.rates
        zone_1_quarterly_payroll = person(
            "employer_ny_mctmt_zone_1_quarterly_payroll_expense", period
        )
        zone_2_quarterly_payroll = person(
            "employer_ny_mctmt_zone_2_quarterly_payroll_expense", period
        )
        zone_1_rate = p.zone_1.calc(zone_1_quarterly_payroll, right=True)
        zone_2_rate = p.zone_2.calc(zone_2_quarterly_payroll, right=True)
        return 4 * (
            zone_1_rate * zone_1_quarterly_payroll
            + zone_2_rate * zone_2_quarterly_payroll
        )
