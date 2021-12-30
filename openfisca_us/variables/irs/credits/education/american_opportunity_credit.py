from openfisca_us.model_api import *


class american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "American Opportunity Credit"
    unit = "currency-USD"
    documentation = "Total value of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#b"

    def formula(tax_unit, period, parameters):
        education = parameters(period).irs.credits.education
        aoc = education.american_opportunity_credit
        person = tax_unit.members
        is_eligible = person(
            "is_eligible_for_american_opportunity_credit", period
        )
        tuition_expenses = (
            person("qualified_tuition_expenses", period) * is_eligible
        )
        maximum_amount_per_student = aoc.amount.calc(tuition_expenses)
        maximum_amount = tax_unit.sum(maximum_amount_per_student)
        phaseout = tax_unit("education_credit_phaseout", period)
        return max_(0, maximum_amount * (1 - phaseout))


class refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable American Opportunity Credit"
    unit = "currency-USD"
    documentation = (
        "Value of the refundable portion of the American Opportunity Credit"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    def formula(tax_unit, period, parameters):
        aoc = parameters(
            period
        ).irs.credits.education.american_opportunity_credit
        return aoc.refundability * tax_unit(
            "american_opportunity_credit", period
        )


class non_refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable American Opportunity Credit"
    unit = "currency-USD"
    documentation = "Value of the non-refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    def formula(tax_unit, period):
        total = tax_unit("american_opportunity_credit", period)
        refundable = tax_unit("refundable_american_opportunity_credit", period)
        return total - refundable


class is_eligible_for_american_opportunity_credit(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for American Opportunity Credit"
    documentation = "Whether the person is eligible for the AOC in respect of qualified tuition expenses for this tax year. The expenses must be for one of the first four years of post-secondary education, and the person must not have claimed the AOC for any four previous tax years."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#b_2"

    def formula(person, period):
        # If the person's filing unit has a claim from Form 8863, use that to determine eligibility.
        return person.tax_unit("e87521", period) > 0


class education_credit_phaseout(Variable):
    value_type = float
    entity = TaxUnit
    label = "Education credit phase-out"
    unit = "/1"
    documentation = "Percentage of the American Opportunity and Lifetime Learning credits which are phased out"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        education = parameters(period).irs.credits.education
        agi = tax_unit("adjusted_gross_income", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phaseout_start = where(
            is_joint,
            education.phaseout.start.joint,
            education.phaseout.start.single,
        )
        phaseout_length = where(
            is_joint,
            education.phaseout.length.joint,
            education.phaseout.length.single,
        )
        excess_agi = max(0, agi - phaseout_start)
        return min_(1, excess_agi / phaseout_length)
