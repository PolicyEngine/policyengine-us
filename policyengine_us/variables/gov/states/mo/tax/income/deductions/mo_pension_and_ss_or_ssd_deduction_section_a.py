from policyengine_us.model_api import *


class mo_pension_and_ss_or_ssd_deduction_section_a(Variable):
    value_type = float
    entity = Person
    label = "MO Pension and Social Security or SS Disability Deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
        "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.124",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # NOTE: Excludes military pensions, per: https://dor.mo.gov/forms/Military%20Reference%20Guide.pdf#page=11
        mo_agi = person("mo_adjusted_gross_income", period)
        tax_unit = person.tax_unit
        tax_unit_mo_agi = tax_unit.sum(mo_agi)
        taxable_social_security_benefits = person(
            "taxable_social_security", period
        )
        tax_unit_taxable_social_security_benefits = tax_unit.sum(
            taxable_social_security_benefits
        )
        agi_in_excess_of_taxable_social_security = (
            tax_unit_mo_agi - tax_unit_taxable_social_security_benefits
        )  # Equivalent to Line 3 of section A and B
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.mo.tax.income.deductions

        # Section A, Public Pension Amounts
        # TODO:
        # unclear reference to "See instructions if Line 3 of Section C is more than $0" here: https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
        public_pension_allowance = p.mo_public_pension_deduction_allowance[
            filing_status
        ]
        agi_over_public_pension__allowance = max_(
            agi_in_excess_of_taxable_social_security
            - public_pension_allowance,
            0,
        )
        public_pension_amount = person("taxable_public_pension_income", period)
        max_social_security_benefit = (
            p.mo_max_social_security_benefit
        )  # Seen on Line 7, Section A
        public_pension_value = min_(
            public_pension_amount, max_social_security_benefit
        )
        ss_or_ssdi_exemption_threshold = p.mo_ss_or_ssdi_exemption_threshold[
            filing_status
        ]

        eligible_ss_or_ssd = person(
            "mo_pension_and_ss_or_ssd_deduction_section_c", period
        )

        # From instructions here: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=17
        adjusted_ss_or_ssdi_value = where(
            (mo_agi - ss_or_ssdi_exemption_threshold) > 0,
            eligible_ss_or_ssd,  # this comes froms the result of section c
            taxable_social_security_benefits,  # this is the unmodified benefits value, from Part 3 - Section C, Line 6
        )
        public_pension_less_ss_deduction = max_(
            public_pension_value - adjusted_ss_or_ssdi_value, 0
        )

        return max_(
            public_pension_less_ss_deduction
            - agi_over_public_pension__allowance,
            0,
        )
