from policyengine_us.model_api import *


class nj_employee_workforce_fund_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employee workforce development contribution"
    documentation = (
        "Combined employee contributions under N.J.S.A. 34:15D-13 and 34:15D-22 "
        "to the Workforce Development Partnership and Supplemental Workforce "
        "Funds, using the employee UI wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    reference = (
        "https://www.nj.gov/labor/ea/employer-services/rate-info/",
        "https://pub.njleg.gov/bills/2000/PL01/152_.PDF#page=2",
    )

    def formula_2015_01_01(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.payroll.workforce_development
        taxable_wages = person("nj_employee_unemployment_taxable_wages", period)
        return p.employee_rate * taxable_wages
