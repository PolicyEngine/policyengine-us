from policyengine_us.model_api import *


class ri_works_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Rhode Island Works dependent care deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/rhode-island/218-RICR-20-00-2.15",
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        # Per 218-RICR-20-00-2.15.5(B)(2): Dependent care expenses deducted
        # up to $200/month for children under age 2
        # up to $175/month for children age 2 and older or an incapacitated
        # adult living in the home and receiving cash assistance
        p = parameters(period).gov.states.ri.dhs.works.income.dependent_care
        person = spm_unit.members

        is_dependent = person("is_tax_unit_dependent", period)
        incapacitated_adult = person("is_adult", period.this_year) & person(
            "is_incapable_of_self_care", period.this_year
        )
        age = person("monthly_age", period)

        care_recipient = is_dependent | incapacitated_adult
        max_per_person = p.amount.calc(age)
        total_max_deduction = spm_unit.sum(max_per_person * care_recipient)

        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])

        return min_(childcare_expenses + adult_care_expenses, total_max_deduction)
