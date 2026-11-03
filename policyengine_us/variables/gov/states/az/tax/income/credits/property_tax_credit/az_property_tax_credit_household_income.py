from policyengine_us.model_api import *


class az_property_tax_credit_household_income(Variable):
    value_type = float
    entity = Household
    label = "Household income for the Arizona property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Household income for the Arizona property tax credit, Form 140PTC Part "
        "1 line J: the az_property_tax_credit_income of every tax unit in the "
        "household, so co-residents who file their own returns count. It can "
        "be negative after a capital loss; the credit schedules then use zero."
    )
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(4), (H)(5)
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=3",
    ]
    defined_for = StateCode.AZ

    def formula(household, period, parameters):
        # ARS 43-1072(H)(4): "household" means "the household of the claimant
        # and such other persons as resided with the claimant in the
        # claimant's homestead during the taxable year"; (H)(5): household
        # income is "all income received by all persons of a household".
        # A.A.C. R15-2C-502(A)(2) and (B): a member is any person residing with
        # the claimant, related or not, and each member's separately
        # determined income is combined. Each tax unit's amount is counted
        # once, through its head (as marginal_tax_rate_helpers sums a tax
        # unit amount over a household).
        person = household.members
        head = person("is_tax_unit_head", period)
        unit_income = person.tax_unit("az_property_tax_credit_income", period)
        return household.sum(unit_income * head)
