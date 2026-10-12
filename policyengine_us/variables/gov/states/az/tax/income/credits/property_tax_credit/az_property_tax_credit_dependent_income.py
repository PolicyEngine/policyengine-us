from policyengine_us.model_api import *


class az_property_tax_credit_dependent_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona property tax credit income of dependents"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Income of the tax unit's dependents for the Arizona property tax credit. "
        "Federal AGI, which az_property_tax_credit_agi starts from, holds only the "
        "income of members who are not dependents; Arizona combines the income of "
        "every member of the household, whether or not the member is a dependent. "
        "A dependent's capital gains and losses are the dependent's Form 140PTC "
        "line D amount, so a net loss counts up to the per-member limit; other "
        "losses count in full."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(4)-(6), (I)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2012_itr12-1.pdf#page=2",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # A.A.C. R15-2C-502(A)(2) and (B): household income combines the
        # separately determined income of each member, "whether or not the
        # person is related to, or a dependent of, the claimant". irs_gross_income
        # counts the same federal sources for members who are not dependents.
        # A dependent's losses are not in federal AGI (loss_ald and
        # limited_capital_loss cover members who are not dependents), so each
        # source is added with its sign: a business, farm, rental, partnership
        # or estate loss offsets the dependent's other income, as ITR 12-1
        # items (3) to (5) use the year's loss. The federal list is not
        # Arizona's: like federal AGI for the other members, it counts
        # unemployment whichever state paid it (ARS 43-1072(I) excludes
        # Arizona's) and leaves out strike benefits and alimony that is not
        # federally taxable.
        sources = parameters(period).gov.irs.gross_income.sources
        income = 0
        for source in sources:
            # ARS 43-1072(I): Social Security benefits are not income.
            # Capital gains and losses, including capital gain distributions,
            # are added below as line D.
            if source in (
                "taxable_social_security",
                "capital_gains",
                "non_sch_d_capital_gains",
            ):
                continue
            income += add(person, period, [source])
        # Form 140PTC line D: a dependent is a household member like any
        # other, so a net capital loss counts, limited to $1,500 for the
        # dependent (A.A.C. R15-2C-502(C)(3)), as it is for the claimant.
        income += person("az_property_tax_credit_capital_gains", period)
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(is_dependent * income)
