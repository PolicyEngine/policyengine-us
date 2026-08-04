from policyengine_us.model_api import *


class co_sales_tax_refund_person_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible individual for the Colorado sales tax refund"
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-2003(1)(a) defines a "qualified individual" via a
        # disjunctive test: (I) has CO income tax liability or files to claim a
        # refund of withheld wages, OR (II) is at least 18 years of age.
        "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-39.pdf",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23",
    )
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.sales_tax_refund
        # Only the head and spouse can be eligible filers (not dependents).
        is_filer = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        # The statute measures age as of December 31 of the year preceding the
        # taxable year; the model approximates this with current-year age.
        age_eligible = person("age", period) >= p.age_threshold
        # Filers that had Colorado tax withheld are also eligible; use employment
        # income as a proxy.
        employment_income_eligible = person("irs_employment_income", period) > 0
        # Per C.R.S. 39-22-2003(1)(a)(I), the tax-liability / files-to-claim-
        # withholding qualifier is AGE-INDEPENDENT (disjunctive with the 18+
        # path in (1)(a)(II)), so no age gate applies here. Because
        # co_income_tax_before_non_refundable_credits is a tax-unit-level value,
        # it qualifies both filers; the joint liability cannot be split per
        # spouse (a documented limitation).
        tax_unit = person.tax_unit
        income_tax_eligible = (
            tax_unit("co_income_tax_before_non_refundable_credits", period) > 0
        )
        return is_filer & (
            age_eligible | employment_income_eligible | income_tax_eligible
        )
