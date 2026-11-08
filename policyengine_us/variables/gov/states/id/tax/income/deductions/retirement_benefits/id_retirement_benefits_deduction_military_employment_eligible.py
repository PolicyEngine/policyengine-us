from policyengine_us.model_api import *


class id_retirement_benefits_deduction_military_employment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Employment income requires a federal return, for the Idaho military retirement benefits deduction"
    documentation = """
    Idaho Code 63-3022A(1)(b)(iii) admits the military retirement benefits of
    a recipient who "was employed during the tax year and received sufficient
    income from such employment to be required to file a federal return under
    section 6012(a)(1) of the Internal Revenue Code". This is true when the
    person's income from employment, by itself, meets the gross income test
    of the federal filing requirement for the person's return, as
    tax_unit_is_required_to_file applies it to a return nobody can claim:
    section 6012(f), more than the standard deduction, for 2018 to 2025, and
    section 6012(a)(1)(A) and (B), at least the basic standard deduction plus
    the additions for age, in other years. On a joint return the threshold is
    the joint one. As in the federal gross income, a loss from one source
    doesn't reduce income from another.
    """
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
        "https://www.law.cornell.edu/uscode/text/26/6012",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits.military.employment
        employment_income = 0
        for source in p.income_sources:
            employment_income = employment_income + max_(
                0, add(person, period, [source])
            )
        employed = employment_income > 0

        # The thresholds of tax_unit_is_required_to_file, for a return
        # nobody can claim.
        p_irs = parameters(period).gov.irs
        exemption_amount = (
            0 if p_irs.income.exemption.suspended else p_irs.income.exemption.amount
        )
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        if p_irs.income.filing_requirement.standard_deduction_rule.applies:
            # Section 6012(f): gross income over the standard deduction, and
            # any gross income on a separate return.
            threshold = where(
                separate,
                exemption_amount,
                tax_unit("standard_deduction", period) + exemption_amount,
            )
            requires_return = employment_income > threshold
        else:
            # Section 6012(a)(1)(A) and (B): gross income of at least the
            # exemption amount for each spouse plus the basic standard
            # deduction, raised by one additional standard deduction for
            # each spouse aged 65 or older. A separate return, or one whose
            # standard deduction is zero under section 63(c)(6), has no
            # exception.
            aged_count = tax_unit("aged_head", period).astype(int) + tax_unit(
                "aged_spouse", period
            ).astype(int)
            basic_threshold = (
                exemption_amount * tax_unit("head_spouse_count", period)
                + tax_unit("basic_standard_deduction", period)
                + tax_unit("bonus_guaranteed_deduction", period)
                + aged_count
                * p_irs.deductions.standard.aged_or_blind.amount[filing_status]
            )
            no_exception = separate | tax_unit("separate_filer_itemizes", period)
            threshold = where(no_exception, exemption_amount, basic_threshold)
            requires_return = employment_income >= threshold
        return p.in_effect & employed & requires_return
