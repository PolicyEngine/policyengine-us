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
    Business losses count within the IRC 461(l) limit, as for the filers.
    It starts from dependent_taxable_ss_magi's income measure and takes out
    the unemployment compensation the dependent excludes under IRC 85(c),
    which applied only in 2020. As in that measure, taxable dependent care
    benefits stay out, and the model attributes no above-the-line deduction
    it records only for the tax unit (health savings account contributions,
    which IRC 223(b)(6) denies to dependents anyway).
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a",
        "https://www.law.cornell.edu/uscode/text/26/1211#b",
        "https://www.law.cornell.edu/uscode/text/26/86#a",
        "https://www.law.cornell.edu/uscode/text/26/85#c",
    )

    def formula(person, period, parameters):
        income, _ = dependent_income_and_deductions(person, period, parameters)
        deductions = [
            PERSON_ABOVE_THE_LINE_DEDUCTIONS[deduction]
            for deduction in parameters(period).gov.irs.ald.deductions
            if deduction in PERSON_ABOVE_THE_LINE_DEDUCTIONS
        ]
        taxable_social_security = person("dependent_taxable_social_security", period)
        # The income measure counts all unemployment compensation received
        # (IRC 86(b)(2)(A)); the dependent's own return leaves out what IRC
        # 85(c) excludes, which taxable_unemployment_compensation figures.
        received = max_(0, person("total_unemployment_compensation", period))
        excluded_unemployment_compensation = max_(
            0, received - person("taxable_unemployment_compensation", period)
        )
        return (
            income
            - excluded_unemployment_compensation
            - add(person, period, deductions)
            + taxable_social_security
        )
