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
        homestead_property_cost = (
            person.spm_unit("housing_cost", period) - rent_expense
        )

        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # Attributing the housing cost equally to each spouse if filing jointly
        applicable_homestead_property_cost = where(
            joint, homestead_property_cost / 2, homestead_property_cost
        )
        homestead_property_allowance = min_(
            applicable_homestead_property_cost, p.homestead
        )

        return where(renter, rent_allowance, homestead_property_allowance)
