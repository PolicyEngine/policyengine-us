from policyengine_us.model_api import *


class medicaid_adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for Medicaid MAGI household rules"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        gross_income = person("medicaid_irs_gross_income", period)
        person_ald_vars = [
            "self_employment_tax_ald_person",
            "self_employed_health_insurance_ald_person",
            "self_employed_pension_contribution_ald_person",
        ]
        ald_sum_person = add(person, period, person_ald_vars)
        all_alds = parameters(period).gov.irs.ald.deductions
        other_alds = [
            ald
            for ald in all_alds
            if ald
            not in (
                "self_employment_tax_ald",
                "self_employed_health_insurance_ald",
                "self_employed_pension_contribution_ald",
            )
        ]
        ald_sum_taxunit = add(person.tax_unit, period, other_alds)
        filing_status = person.tax_unit("filing_status", period)
        frac = where(
            filing_status == filing_status.possible_values.JOINT,
            0.5,
            1.0,
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        shared_ald = head_or_spouse * ald_sum_taxunit * frac
        agi = gross_income - ald_sum_person - shared_ald

        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            agi += head_or_spouse * basic_income * frac

        return agi
