from policyengine_us.model_api import *


class student_loan_interest_ald_magi(Variable):
    value_type = float
    entity = Person
    label = "Modified adjusted gross income for the student loan interest ALD"
    unit = USD
    definition_period = YEAR
    documentation = "Above-the-line deduction for student loan interest"
    reference = "https://www.law.cornell.edu/uscode/text/26/221#b_2_C"
    defined_for = "student_loan_interest_ald_eligible"

    def formula(person, period, parameters):
        p_irs = parameters(period).gov.irs
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross_income_sources = p_irs.gross_income.sources
        # Unemployment compensation is not considered in MAGI
        gross_income = [
            income_source
            for income_source in gross_income_sources
            if income_source
            not in p_irs.ald.student_loan_interest.magi.excluded_gross_income_sources
        ]
        total_gross_income = 0
        for source in gross_income:
            total_gross_income += not_dependent * max_(
                0, add(person, period, [source])
            )
        # Modified gross income is calculated with certain deductions excluded
        person_alds = p_irs.ald.student_loan_interest.magi.person_alds
        person_ald_vars = [f"{ald}_person" for ald in person_alds]
        ald_sum_person = add(person, period, person_ald_vars)
        all_alds = p_irs.ald.deductions
        other_alds = list(
            set(all_alds)
            - set(person_alds)
            - set(p_irs.ald.student_loan_interest.magi.excluded_alds)
        )
        ald_sum_taxunit = add(person.tax_unit, period, other_alds)
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        frac = where(joint, 0.5, 1.0)
        ald_sum_taxunit_shared = not_dependent * ald_sum_taxunit * frac

        modified_adjusted_gross_income = (
            total_gross_income - ald_sum_person - ald_sum_taxunit_shared
        )
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            # split basic income evenly between head and spouse
            basic_income_shared = not_dependent * basic_income * frac
            modified_adjusted_gross_income += basic_income_shared
        # Combine the income for units filing jointly
        return modified_adjusted_gross_income
