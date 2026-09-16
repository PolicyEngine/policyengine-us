from policyengine_us.model_api import *


class in_civil_service_annuity_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana civil service annuity deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://iga.in.gov/laws/2024/ic/titles/6#6-3-2-3.7",
        "https://forms.in.gov/Download.aspx?id=16915#page=19",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.deductions.civil_service_annuity
        )
        age = person("age", period)
        meets_age = age >= p.min_age
        # IC 6-3-2-3.7 allows a deduction for a federal civil service annuity
        # included in federal AGI, up to $16,000 per qualifying individual (age 62+),
        # minus Social Security and railroad retirement benefits.
        # Bounding by taxable_public_pension_income ensures the deduction does not
        # exceed the public pension included in federal AGI and that taxpayers without
        # federal civil service pensions receive no deduction.
        qualifying_annuity = min_(
            person("taxable_federal_pension_income", period),
            person("taxable_public_pension_income", period),
        )
        ss_and_rr = person("social_security", period) + person(
            "railroad_benefits", period
        )
        capped_annuity = min_(qualifying_annuity, p.cap)
        person_deduction = meets_age * max_(0, capped_annuity - ss_and_rr)
        return tax_unit.sum(person_deduction)
