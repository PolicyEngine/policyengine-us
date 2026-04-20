from policyengine_us.model_api import *


class student_loan_interest_ald_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Student loan interest ALD"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/221"
    documentation = (
        "Eligibility for the student loan interest above-the-line deduction. "
        "Per IRC § 221, the taxpayer must not file as Married Filing Separately "
        "(§ 221(e)(2)) and cannot be claimed as a dependent (§ 221(c)). "
        "The MAGI phase-out is handled separately in the deduction calculation. "
        "Note: While § 221(d)(3) references § 25A(b)(3) for the definition of "
        "'eligible student', this refers to the student's status when the loan "
        "was originally taken out, not current-year AOC eligibility. A person "
        "who graduated years ago remains eligible to deduct student loan interest."
    )

    def formula(person, period, parameters):
        # Per IRC § 221(c), taxpayer cannot be claimed as a dependent
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Per IRC § 221(e)(2), taxpayer cannot file as Married Filing Separately
        filing_status = person.tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return head_or_spouse & ~separate
