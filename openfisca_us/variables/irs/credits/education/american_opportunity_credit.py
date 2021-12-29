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
        is_eligible = tax_unit.members(
            "is_eligible_for_american_opportunity_credit", period
        )
        tuition_expenses = (
            tax_unit.members("qualified_tuition_expenses", period)
            * is_eligible
        )
        maximum_amount_per_student = aoc.amount.calc(tuition_expenses)
        maximum_amount = tax_unit.sum(maximum_amount_per_student)
        agi = tax_unit("adjusted_gross_income", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phaseout_start = where(
            is_joint,
            education.phaseout.start.single,
            education.phaseout.start.joint,
        )
        excess_agi = max(0, agi - phaseout_start)
        percentage_reduction = excess_agi / maximum_amount
        return max_(0, maximum_amount * (1 - percentage_reduction))


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
