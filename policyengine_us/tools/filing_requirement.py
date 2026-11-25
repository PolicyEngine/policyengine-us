"""Gross income thresholds of the federal filing requirement, 26 U.S.C. 6012."""

import numpy as np


def section_6012_gross_income_thresholds(tax_unit, period, parameters):
    """The two gross income thresholds of section 6012, for each return.

    `tax_unit` takes a TaxUnit population, or a person's `tax_unit`
    projector, which returns each value for the person's tax unit.
    tax_unit_is_required_to_file adds the tests for a filer someone can claim
    as a dependent and for a spouse who loses the joint-return exception.

    Returns `(standard_deduction_threshold, basic_threshold)`:

    - Section 6012(f), for 2018 to 2025: gross income over the standard
      deduction, which includes the additional standard deduction for age
      and for blindness, requires a return. A married individual filing
      separately must file with any gross income, so that return's threshold
      equals the exemption amount. Compare with `>`.
    - Section 6012(a)(1)(A) and (B), from 2026 (and before 2018): gross
      income of at least the exemption amount for each spouse plus the basic
      standard deduction, raised by one additional standard deduction for
      each spouse aged 65 or older (section 63(f)(1)), requires a return.
      Blindness doesn't raise it. The WFTCA contributed reform's bonus
      guaranteed deduction increases the basic standard deduction (zero
      unless that reform applies). For a filer someone can claim as a
      dependent, basic_standard_deduction already gives the section 63(c)(5)
      limited amount. A married individual filing separately has no
      exception, and with an exemption amount of zero, (A) reaches even an
      individual with no gross income, since no gross income falls "less
      than" zero. Section 6012(a)(1)(C)(ii) withholds the (A) exception from
      "any individual ... for whom the standard deduction is zero under
      section 63(c)(6)". separate_filer_itemizes gives PE-US's only 63(c)(6)
      path, so that threshold falls to the exemption amount, without the age
      addition, whatever the filing status. Compare with `>=`.
    """
    p = parameters(period).gov.irs
    exemption_amount = 0 if p.income.exemption.suspended else p.income.exemption.amount
    filing_status = tax_unit("filing_status", period)
    separate = filing_status == filing_status.possible_values.SEPARATE

    standard_deduction_threshold = np.where(
        separate,
        exemption_amount,
        tax_unit("standard_deduction", period) + exemption_amount,
    )

    aged_count = tax_unit("aged_head", period).astype(int) + tax_unit(
        "aged_spouse", period
    ).astype(int)
    exceptions_threshold = (
        exemption_amount * tax_unit("head_spouse_count", period)
        + tax_unit("basic_standard_deduction", period)
        + tax_unit("bonus_guaranteed_deduction", period)
        + aged_count * p.deductions.standard.aged_or_blind.amount[filing_status]
    )
    no_exception = separate | tax_unit("separate_filer_itemizes", period)
    basic_threshold = np.where(no_exception, exemption_amount, exceptions_threshold)
    return standard_deduction_threshold, basic_threshold
