from policyengine_us.model_api import *


class pa_tanf_earned_income_after_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF earned income after deductions per person"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "http://services.dpw.state.pa.us/oimpolicymanuals/cash/160_Income_Deductions/160_2_TANF_Earned_Income_Deductions.htm",
        "https://www.law.cornell.edu/regulations/pennsylvania/55-Pa-Code-SS-183-94",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.income.deductions

        gross_earned = person("tanf_gross_earned_income", period)
        disregard_eligible = person.spm_unit(
            "pa_tanf_disregard_eligible", period
        )

        after_eid = gross_earned * (1 - p.earned_income_disregard.percentage)
        after_wed = max_(after_eid - p.work_expense.additional, 0)

        return where(disregard_eligible, after_wed, gross_earned)
