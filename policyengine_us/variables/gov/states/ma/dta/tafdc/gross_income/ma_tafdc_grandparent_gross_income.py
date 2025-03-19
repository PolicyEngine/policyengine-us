from policyengine_us.model_api import *


class ma_tafdc_grandparent_gross_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) grandparent earned income"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/68-how-grandparent-income-counted-towards-baby-teen-parent"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income
        is_grandparent = person("is_grandparent_of_filer_or_spouse", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        # Calculate total income by summing up earned and unearned income sources
        earned_income_sources = p.earned
        unearned_income_sources = p.unearned
        all_income_sources = earned_income_sources + unearned_income_sources
        total_income = add(person, period, all_income_sources)
        teen_parent_present = person.spm_unit.any(
            person("ma_tafdc_eligible_teen_parent", period)
        )
        deduction = where(
            teen_parent_present, fpg * p.deductions.grandparent_income, 0
        )
        return is_grandparent * max_(0, total_income - deduction)
