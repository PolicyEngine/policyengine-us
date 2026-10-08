from policyengine_us.model_api import *

# Above-the-line deductions recorded only for the tax unit, with no person-level
# amount to attribute them by. Their amount is divided equally between the head
# and spouse.
EQUALLY_DIVIDED_DEDUCTIONS = (
    # Tuition and fees (26 USC 222, through 2020) the taxpayer paid for
    # themself, their spouse or a dependent, under one limit for the return.
    "capped_qualified_tuition_expenses_ald",
    # Domestic production activities (26 USC 199, through 2017), an input for
    # the tax unit.
    "domestic_production_ald",
    # Income of a bona fide resident of a possession (26 USC 931) or of Puerto
    # Rico (26 USC 933), inputs for the tax unit.
    "specified_possession_income",
    "puerto_rico_income",
)


class above_the_line_deductions_person(Variable):
    value_type = float
    entity = Person
    label = "Above-the-line deductions for each person"
    unit = USD
    documentation = (
        "Each person's above-the-line deductions. The head's and spouse's "
        "amounts divide the tax unit's above_the_line_deductions between them. "
        "Each has their own person-level deductions, such as their IRA "
        "deduction, educator expenses and early withdrawal penalty, and their "
        "own part of each tax-unit deduction that has a person-level amount "
        "(<deduction>_person), such as self-employment tax, alimony paid and "
        "business and capital losses. A deduction recorded only for the tax "
        "unit is divided equally between them. A tax unit dependent's amount "
        "is their own person-level deductions, for their own return, other "
        "than amounts that are the filer's even when recorded on the "
        "dependent (gov.irs.ald.filer_amounts_recorded_on_dependents), which "
        "the head and spouse divide equally; the dependent's losses and "
        "tax-unit-only deductions are not modeled here."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filer = ~person("is_tax_unit_dependent", period)
        p = parameters(period).gov.irs.ald
        total = 0
        # Sum in a fixed order so float32 results do not depend on the hash
        # seed.
        for deduction in sorted(set(p.deductions)):
            variable = person.entity.get_variable(deduction, check_existence=True)
            if variable.entity.is_person:
                # The person's own deduction. For the head and spouse it is
                # their part of the return's sum over non-dependents.
                amount = person(deduction, period)
                if deduction in p.filer_amounts_recorded_on_dependents:
                    # The filer's amount even when recorded on a dependent, so
                    # it is not on the dependent's own return. Which of the
                    # head and spouse it belongs to is not recorded, so a
                    # dependent's amount is divided equally between them.
                    on_dependents = tax_unit.sum(~filer * amount)
                    equal_share = filer_share(person, period, 0 * amount)
                    amount = filer * amount + on_dependents * equal_share
                total = total + amount
                continue
            return_amount = tax_unit(deduction, period)
            person_variable = f"{deduction}_person"
            if person.entity.get_variable(person_variable) is None:
                equal_share = filer_share(person, period, 0 * return_amount)
                total = total + return_amount * equal_share
                continue
            own = person(person_variable, period)
            filer_own = filer * own
            # The return's amount is the sum of the head's and spouse's own
            # amounts, unless it was set directly. Any difference is divided
            # in proportion to their own amounts, or equally when neither has
            # one, so the parts always add up to the return's amount.
            difference = return_amount - tax_unit.sum(filer_own)
            share = filer_share(person, period, own)
            total = total + where(filer, filer_own + difference * share, own)
        # The head's and spouse's parts add up to above_the_line_deductions.
        # If that is set directly, the difference is divided in proportion to
        # their parts, or equally when neither has any.
        filer_parts = filer * total
        difference = tax_unit("above_the_line_deductions", period) - tax_unit.sum(
            filer_parts
        )
        share = filer_share(person, period, total)
        return where(filer, filer_parts + difference * share, total)
