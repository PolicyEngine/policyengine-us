from policyengine_us.model_api import *


class student_loan_interest_ald(Variable):
    value_type = float
    entity = Person
    label = "Student loan interest ALD"
    unit = USD
    definition_period = YEAR
    documentation = "Above-the-line deduction for student loan interest"
    reference = "https://www.law.cornell.edu/uscode/text/26/221"

    def formula(person, period, parameters):
        interest = person("student_loan_interest", period)
        p = parameters(period).gov.irs.ald.student_loan_interest
        filing_status = person.tax_unit("filing_status", period)
        capped_interest = min_(interest, p.cap[filing_status])
        # The reduction is based on the taxpayer's modified adjusted gross income (MAGI)
        # which is defined as AGI less ALDs
        p_irs = parameters(period).gov.irs
        not_dependent = ~person("is_tax_unit_dependent", period)
        gross_income_sources = p_irs.gross_income.sources
        # Unemployment compensation is not considered in MAGI
        gross_income = [
            income_source
            for income_source in gross_income_sources
            if income_source != "taxable_unemployment_compensation"
        ]
        total_gross_income = 0
        for source in gross_income:
            total_gross_income += not_dependent * max_(
                0, add(person, period, [source])
            )
        # Modified gross income is calculated with certain deductions excluded
        PERSON_ALDS = [
            "self_employment_tax_ald",
            "self_employed_health_insurance_ald",
            "self_employed_pension_contribution_ald",
        ]
        EXCLUDED_ALDS = ["student_loan_interest_ald", "puerto_rico_income"]
        person_ald_vars = [f"{ald}_person" for ald in PERSON_ALDS]
        ald_sum_person = add(person, period, person_ald_vars)
        all_alds = p_irs.ald.deductions
        other_alds = list(
            set(all_alds) - set(PERSON_ALDS) - set(EXCLUDED_ALDS)
        )
        ald_sum_taxunit = add(person.tax_unit, period, other_alds)
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
        combined_magi = where(
            joint,
            person.tax_unit.sum(modified_adjusted_gross_income),
            modified_adjusted_gross_income,
        )

        income_excess = max_(
            0, combined_magi - p.reduction.start[filing_status]
        )
        divisor = p.reduction.divisor[filing_status]
        reduction_rate = np.zeros_like(divisor)
        mask = divisor != 0
        reduction_rate[mask] = income_excess[mask] / divisor[mask]
        reduction_amount = capped_interest * reduction_rate
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return max_(capped_interest - reduction_amount, 0) * head_or_spouse
