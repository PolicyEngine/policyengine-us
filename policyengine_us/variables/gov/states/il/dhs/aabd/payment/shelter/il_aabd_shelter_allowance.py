from policyengine_us.model_api import *


class il_aabd_shelter_allowance(Variable):
    value_type = float
    entity = Person
    label = (
        "Illinois Aid to the Aged, Blind or Disabled (AABD) shelter allowance"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.248",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.payment.shelter_allowance
        rent_expense = person("rent", period)
        renter = rent_expense > 0
        rent_allowance = min_(rent_expense, p.rent)
        # Housing cost = rent + property tax + homeowners insurance + HOA fees.
        homestead_property_cost = (
            person.spm_unit("housing_cost", period) - rent_expense
        )
        homestead_property_allowance = min_(
            homestead_property_cost, p.homestead
        )

        total_allowance = where(
            renter, rent_allowance, homestead_property_allowance
        )
        # Prorate the total shelter_allowance across all household members
        size = person.spm_unit("spm_unit_size", period)
        return total_allowance / size
