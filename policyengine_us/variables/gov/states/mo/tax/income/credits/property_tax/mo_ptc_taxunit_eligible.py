from policyengine_us.model_api import *


class mo_ptc_taxunit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Missouri property tax credit taxunit eligible"
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=57542",
        "https://dor.mo.gov/forms/MO-PTC%20Instructions_2025.pdf#page=2",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        # RSMo 135.010(1) claimant pathways; the first three are satisfied by
        # the claimant or spouse.
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        elderly = (age_head >= p.age_threshold) | (age_spouse >= p.age_threshold)
        # 135.010(2) defines "disabled" by inability to engage in substantial
        # gainful activity, without requiring SSI participation.
        disabled = tax_unit("head_is_disabled", period) | tax_unit(
            "spouse_is_disabled", period
        )
        military_disabled = tax_unit("military_disabled_head", period) | tax_unit(
            "military_disabled_spouse", period
        )
        # The surviving-spouse pathway applies to the claimant only: the
        # claimant must be 60 or older and have received surviving spouse
        # Social Security benefits themselves. The model treats the tax
        # unit head as the filer/claimant, so the same-person test runs on
        # the head; the other three pathways are claimant-or-spouse.
        person = tax_unit.members
        head_survivor_benefits = tax_unit.sum(
            person("social_security_survivors", period)
            * person("is_tax_unit_head", period)
        )
        aged_survivor = (age_head >= p.aged_survivor_min_age) & (
            head_survivor_benefits > 0
        )
        categorical = elderly | disabled | military_disabled | aged_survivor
        # RSMo 135.025 bases the credit on property taxes accrued and rent
        # constituting property taxes accrued; DOR routes claimants who paid
        # neither to not eligible.
        rent = add(tax_unit, period, ["rent"])
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        paid_rent_or_property_tax = (rent + property_tax) > 0
        # RSMo 135.030(1) caps net income at the maximum upper limit.
        # DOR forms round entries half-up to whole dollars.
        net_income = np.floor(tax_unit("mo_ptc_net_income", period) + 0.5)
        income_eligible = net_income <= tax_unit("mo_ptc_income_limit", period)
        return categorical & paid_rent_or_property_tax & income_eligible
