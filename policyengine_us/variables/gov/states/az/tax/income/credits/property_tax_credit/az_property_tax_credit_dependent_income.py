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
        "every member of the household, whether or not the member is a dependent."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(4)-(6), (I)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
    ]
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # A.A.C. R15-2C-502(A)(2) and (B): household income combines the
        # separately determined income of each member, "whether or not the
        # person is related to, or a dependent of, the claimant". irs_gross_income
        # counts the same federal sources for members who are not dependents.
        # Only positive amounts are added: federal AGI (loss_ald) already
        # deducts every member's losses, dependents' included. The federal
        # list is not Arizona's: like federal AGI for the other members, it
        # counts unemployment whichever state paid it (ARS 43-1072(I) excludes
        # Arizona's) and leaves out estate income, strike benefits and
        # alimony that is not federally taxable.
        sources = parameters(period).gov.irs.gross_income.sources
        income = 0
        for source in sources:
            # ARS 43-1072(I): Social Security benefits are not income.
            if source == "taxable_social_security":
                continue
            income += max_(0, add(person, period, [source]))
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(is_dependent * income)
