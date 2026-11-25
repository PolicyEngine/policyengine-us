from policyengine_us.model_api import *


class ma_rent_deduction_qualifying_rent_paid(Variable):
    """Personally paid rent established by source-qualified expense receipts.

    Receipts identify the payer, return, Massachusetts principal residence and
    qualifying periods. They exclude third-party payments, separately charged
    utilities, furnishings and parking, unapplied deposits or advance rent,
    condominium or cooperative charges, and nonqualifying lodging or periods.
    No population imputation or automatic qualification is supplied here.
    """

    value_type = float
    entity = Person
    label = "Personally paid qualifying Massachusetts rent for the rent deduction"
    unit = USD
    definition_period = YEAR
    default_value = -1
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section3",
        "https://www.mass.gov/info-details/deductions-on-rent-paid-in-massachusetts",
    )
