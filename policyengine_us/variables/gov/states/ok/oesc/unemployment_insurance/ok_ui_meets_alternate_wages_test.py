from policyengine_us.model_api import *


class ok_ui_meets_alternate_wages_test(Variable):
    value_type = bool
    entity = Person
    label = "Meets the Oklahoma UI alternate monetary eligibility test"
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=56"
    )

    def formula(person, period, parameters):
        base_period_taxable_wages = person("ok_ui_base_period_taxable_wages", period)
        base_period_total_wages = person("ok_ui_base_period_total_wages", period)
        taxable_wage_base = parameters(
            period
        ).gov.states.ok.tax.payroll.unemployment.taxable_wage_base
        has_taxable_wages = base_period_taxable_wages > 0
        meets_wage_base = base_period_total_wages >= taxable_wage_base
        return has_taxable_wages & meets_wage_base
