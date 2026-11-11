from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_ss_magi import (
    PERSON_ABOVE_THE_LINE_DEDUCTIONS,
    dependent_income_and_deductions,
)


class dependent_adjusted_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Dependent's adjusted gross income"
    unit = USD
    documentation = """
    The adjusted gross income of IRC 62 on a tax unit dependent's own return:
    their gross income with business, rental, farm, partnership and estate
    losses, and capital losses within the IRC 1211(b) limit, netted; less
    their own above-the-line deductions; plus their taxable Social Security.
    The IRC 461(l) limit on excess business losses is not applied. It
    shares dependent_taxable_ss_magi's income measure, so unemployment
    compensation counts in full (the IRC
    85(c) exclusion applied only in 2020), taxable dependent care benefits
    are left out, and above-the-line deductions the model records only for
    the tax unit (health savings account contributions, which IRC 223(b)(6)
    denies to dependents anyway) are not attributed to dependents.
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.law.cornell.edu/uscode/text/26/86#a",
    )

    def formula(person, period, parameters):
        income, _ = dependent_income_and_deductions(person, period, parameters)
        deductions = [
            PERSON_ABOVE_THE_LINE_DEDUCTIONS[deduction]
            for deduction in parameters(period).gov.irs.ald.deductions
            if deduction in PERSON_ABOVE_THE_LINE_DEDUCTIONS
        ]
        taxable_social_security = person("dependent_taxable_social_security", period)
        return income - add(person, period, deductions) + taxable_social_security
