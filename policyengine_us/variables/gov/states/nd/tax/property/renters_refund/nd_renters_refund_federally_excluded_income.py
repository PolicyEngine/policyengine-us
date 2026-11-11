from policyengine_us.model_api import *


class nd_renters_refund_federally_excluded_income(Variable):
    value_type = float
    entity = Person
    label = "North Dakota Renter's Refund market income excluded by federal law"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The parts of a person's market_income components that federal law "
        "leaves out of gross income, which N.D.C.C. 57-02-08.1(5)(c) excludes "
        "from renter's refund income: the payroll deductions federal law "
        "excludes from wages, tax-exempt interest, the nontaxable part of "
        "pensions and of retirement account distributions, disability "
        "benefits from a plan the recipient paid for, and alimony under a "
        "divorce or separation instrument executed after 2018. Each part is at "
        "least zero and at most the market_income component it comes from. "
        "nd_renters_refund_income also subtracts the federal exclusions the "
        "model deducts above the line."
    )
    reference = (
        # N.D.C.C. 57-02-08.1(5)(c).
        "https://ndlegis.gov/cencode/t57c02.pdf#page=16",
        # Payroll deductions: elective deferrals (402(e)(3), 402(g)(1)),
        # 403(b) contributions, employer health coverage and HSA
        # contributions (106(a), 106(d)), cafeteria plans (125(a)) and
        # dependent care assistance (129(a)).
        "https://www.law.cornell.edu/uscode/text/26/402",
        "https://www.law.cornell.edu/uscode/text/26/403#b_1",
        "https://www.law.cornell.edu/uscode/text/26/106",
        "https://www.law.cornell.edu/uscode/text/26/125#a",
        "https://www.law.cornell.edu/uscode/text/26/129#a",
        # Interest on state and local bonds.
        "https://www.law.cornell.edu/uscode/text/26/103#a",
        # Pensions and retirement accounts: the investment in the contract
        # (72(b)(1)), rollovers (402(c)(1), 403(b)(8), 408(d)(3)), and
        # qualified Roth distributions (402A(d)(1), 408A(d)(1)).
        "https://www.law.cornell.edu/uscode/text/26/72#b_1",
        "https://www.law.cornell.edu/uscode/text/26/403#b_8",
        "https://www.law.cornell.edu/uscode/text/26/402A#d_1",
        "https://www.law.cornell.edu/uscode/text/26/408#d",
        "https://www.law.cornell.edu/uscode/text/26/408A#d_1",
        # Disability benefits from a plan the recipient paid for.
        "https://www.law.cornell.edu/uscode/text/26/104#a_3",
        # Alimony under an instrument executed after 2018.
        "https://www.irs.gov/taxtopics/tc452",
    )
    defined_for = StateCode.ND

    def formula(person, period, parameters):
        def excluded_part(component, excluded):
            # Never negative, and never more than the market_income component
            # the amount comes from, so an input that reports only the
            # component's total keeps all of it as income.
            return min_(max_(excluded, 0), max_(component, 0))

        # Federal gross income counts wages as irs_employment_income, which
        # subtracts the pre-tax payroll deductions in pre_tax_contributions
        # (traditional 401(k) and 403(b) deferrals, health premiums and HSA
        # contributions through payroll, and dependent care assistance), plus
        # the dependent care assistance above the IRC 129 limit. Pre-tax
        # premiums leave income here, and itemized_medical_expenses leaves
        # them out, so neither subtracts a premium the other has.
        wages = person("employment_income", period)
        counted_wages = person("irs_employment_income", period) + person(
            "taxable_dependent_care_benefits", period
        )
        payroll_exclusions = excluded_part(wages, wages - counted_wages)
        # Interest on state and local bonds (IRC 103(a)).
        interest = excluded_part(
            person("interest_income", period),
            person("tax_exempt_interest_income", period),
        )
        # The investment in the contract and rollovers from public and private
        # employer pensions (IRC 72(b)(1), 402(c)(1)).
        pensions = excluded_part(
            person("pension_income", period),
            person("tax_exempt_pension_income", period),
        )
        # Qualified distributions from Roth IRAs and from designated Roth
        # accounts in 401(k) and 403(b) plans, rollovers, and nondeductible IRA
        # and SEP contributions returned (IRC 402A(d)(1), 402(c)(1), 403(b)(8),
        # 408(d), 408A(d)(1)).
        retirement_distributions = excluded_part(
            person("retirement_distributions", period),
            person("tax_exempt_retirement_distributions", period),
        )
        # Benefits from a plan the recipient paid for (IRC 104(a)(3)).
        disability_benefits = excluded_part(
            person("disability_benefits", period),
            person("tax_exempt_disability_benefits", period),
        )
        # Federal gross income leaves out alimony under an instrument executed
        # after 2018 (Pub. L. 115-97 section 11051); taxable_alimony_income
        # holds the rest.
        alimony = person("alimony_income", period)
        excluded_alimony = excluded_part(
            alimony, alimony - person("taxable_alimony_income", period)
        )
        return (
            payroll_exclusions
            + interest
            + pensions
            + retirement_distributions
            + disability_benefits
            + excluded_alimony
        )
