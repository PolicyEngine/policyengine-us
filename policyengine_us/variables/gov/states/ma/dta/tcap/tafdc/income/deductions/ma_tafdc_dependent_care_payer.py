from policyengine_us.model_api import *


class ma_tafdc_dependent_care_payer(Variable):
    value_type = bool
    entity = Person
    label = "Pays the dependent care expenses for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) dependent care deduction"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275",  # (A)
        "https://eohhs.ehs.state.ma.us/DTA/PolicyOnline/BEACON5/%21SSL%21/WebHelp/TAFDC/Employment/Emp_DepCareExTAFDC.htm",
    )
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        # Per 106 CMR 704.275(A), an employed applicant or client receives
        # the deduction for the expenditure on care, and DTA's BEACON help
        # applies it as a deduction for the client incurring the expense.
        # The SPM unit's care expenses do not record who pays them, so the
        # payer is the head or spouse with the highest gross earnings (the
        # first such member when earnings are equal). Set this variable to
        # name the member who pays.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        earnings = person("ma_tcap_gross_earned_income", period)
        rank = person.get_rank(person.spm_unit, -earnings, head_or_spouse)
        return rank == 0
