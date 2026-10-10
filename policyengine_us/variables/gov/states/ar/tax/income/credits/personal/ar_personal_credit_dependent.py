from policyengine_us.model_api import *


class ar_personal_credit_dependent(Variable):
    value_type = float
    entity = Person
    label = "Arkansas personal tax credit dependent amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/2005/Public/ACT675.pdf#page=8",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        # Ark. Code 26-51-501 defines the dependent for this credit by IRC
        # 152 (Act 675 of 2005, sec. 14), and under IRC 152(b)(1) a return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents. The filers' own credits remain.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        dependent = person("is_tax_unit_dependent", period) & ~filer_is_dependent
        p = parameters(period).gov.states.ar.tax.income.credits.personal.amount
        return dependent * p.base
