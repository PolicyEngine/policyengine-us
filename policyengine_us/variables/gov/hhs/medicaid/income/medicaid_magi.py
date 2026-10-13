from policyengine_us.model_api import *


def magi_household_income(tax_unit, period, parameters, counted_dependents):
    """The modified AGI of a tax unit's head and spouse plus that of the
    dependents `counted_dependents` (a person-level mask) selects, before
    any floor at zero.

    Tax unit AGI already leaves dependents' income out, so each person-level
    MAGI addition is summed over the head and spouse only, and a counted
    dependent's whole modified AGI, their own AGI and additions, is added
    signed, as Form 8962 line 3 combines the two "even if one or both of them
    are negative".
    """
    additions = parameters(period).gov.hhs.medicaid.income.modification
    filer_magi = tax_unit("adjusted_gross_income", period) + tax_unit_non_dep_add(
        tax_unit, period, additions
    )
    person = tax_unit.members
    person_level_additions = [
        addition
        for addition in additions
        if tax_unit.entity.get_variable(addition, check_existence=True).entity.is_person
    ]
    dependent_magi = person("medicaid_adjusted_gross_income_person", period) + add(
        person, period, person_level_additions
    )
    counted = person("is_tax_unit_dependent", period) & counted_dependents
    return filer_magi + tax_unit.sum(counted * dependent_magi)


class medicaid_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Medicaid/CHIP/ACA-related Modified AGI"
    unit = USD
    documentation = (
        "Medicaid/CHIP/ACA-related household income for this tax unit: the "
        "modified AGI of the head and spouse, plus the modified AGI of each "
        "tax unit dependent who is required to file a return "
        "(medicaid_person_is_required_to_file), floored at zero. A dependent "
        "who is not required to file adds nothing, whether or not they file, "
        "so their tax-exempt interest and Social Security, such as a child's "
        "survivor benefits, stay out. Social Security counts toward that "
        "filing requirement only to the extent it is taxable."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#e_14_G",  # Medicaid law pointing to IRC
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2",  # IRC defining income
        "https://www.ecfr.gov/current/title-26/section-1.36B-1#p-1.36B-1(e)(1)",
        "https://www.ecfr.gov/current/title-42/section-435.603#p-435.603(d)(2)",
        # Instructions for Form 8962 (2025), Worksheet 1-2 and line 3.
        "https://www.irs.gov/pub/irs-prior/i8962--2025.pdf#page=8",
    )

    def formula(tax_unit, period, parameters):
        required_to_file = tax_unit.members(
            "medicaid_person_is_required_to_file", period
        )
        income = magi_household_income(tax_unit, period, parameters, required_to_file)
        return max_(0, income)
