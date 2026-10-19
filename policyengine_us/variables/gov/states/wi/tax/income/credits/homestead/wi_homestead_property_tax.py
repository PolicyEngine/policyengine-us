from policyengine_us.model_api import *


class wi_homestead_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit property tax amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf#page=2",
        # Wis. Stat. 71.52(4), (7) and (8)
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/53/2/d",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Property taxes on a homestead the claimant or a household member
        # owns (71.52(7)) and rent the claimant and household pay (71.52(8)).
        # The household is the claimant and spouse (71.52(4)), so a
        # dependent's property taxes and rent do not count.
        # A dependent age 62 or older may file a separate claim under
        # 71.53(2)(d). This tax-unit model does not represent that separate
        # claim, so their taxes and rent are not credited to anyone here.
        ptax_owner = tax_unit_non_dep_add(tax_unit, period, ["real_estate_taxes"])
        rent = tax_unit_non_dep_add(tax_unit, period, ["rent"])
        p = parameters(period).gov.states.wi.tax.income.credits
        ptax_renter = rent * p.homestead.property_tax.rent_ratio
        return ptax_owner + ptax_renter
