from policyengine_us.model_api import *


class tn_elderly_property_tax_relief_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tennessee elderly property tax relief income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual income from all sources under T.C.A. 67-5-702(a)(2), as Rule "
        "0600-03-.08(3) defines it: federal adjusted gross income plus the "
        "listed sources that are not taxable by IRS standards, with Social "
        "Security and Railroad Retirement benefits counted after the Medicare "
        "Part B premium withheld from them. Covers the head and spouse of "
        "the tax unit. The statute also counts a spouse who files separately "
        "and other owners of the home, who are in other tax units here."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-0600-03-.08",
        # PDF pages 1-2
        "https://www.comptroller.tn.gov/content/dam/cot/pa/documents/manualsandreports/bulletins-and-summaries/Bulletin2019-01CountingIncomeforTaxReliefandTaxFreeze(12-9-2019).pdf#page=1",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf#page=2",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf#page=3",
    )
    defined_for = StateCode.TN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.tn.tax.property.elderly_property_tax_relief
        person = tax_unit.members
        filer = ~person("is_tax_unit_dependent", period)
        # Rule 0600-03-.08(3): "When determining the income using a tax
        # return, the adjusted gross income amount is used. This amount is
        # added to any income sources specified above which may not be
        # taxable by IRS standards." Bulletin 2019-01 (page 2) allows the
        # Schedule 1 adjustments, which adjusted_gross_income subtracts.
        agi = tax_unit("adjusted_gross_income", period)
        # Sources are summed over the head and spouse; a dependent's income
        # is on the dependent's own return.
        listed_sources = tax_unit_non_dep_add(
            tax_unit, period, p.nontaxable_income.sources
        )
        # The rule lists alimony. Federal adjusted gross income holds
        # alimony under divorce instruments executed before 2019
        # (taxable_alimony_income); the rest is added here.
        alimony = person("alimony_income", period)
        nontaxable_alimony = max_(alimony - person("taxable_alimony_income", period), 0)
        # The rule counts Social Security "after the Medicare deduction" and
        # retirement benefits after healthcare insurance premiums.
        # medicare_part_b_premium is the premium the person pays, zero when a
        # Medicare Savings Program or Medicaid pays it, so nothing is
        # withheld. It comes off the Social Security and Railroad Retirement
        # benefits it is withheld from, and no further. When it exceeds the
        # nontaxable Social Security, the excess comes off the taxable part
        # that adjusted gross income holds.
        withholding_benefits = max_(person("social_security", period), 0) + max_(
            person("railroad_benefits", period), 0
        )
        medicare_deduction = min_(
            person("medicare_part_b_premium", period), withholding_benefits
        )
        return (
            agi
            + listed_sources
            + tax_unit.sum((nontaxable_alimony - medicare_deduction) * filer)
        )
