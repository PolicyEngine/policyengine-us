from policyengine_us.model_api import *


class in_blind_disabled_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana blind or disabled property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=143",
        "https://www.in.gov/dlgf/files/2025-memos/250612-Cockerill-Memo-Legislation-Affecting-Deductions%2C-Exemptions%2C-and-Credits.pdf#page=4",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # SEA 1 (2025) IC 6-1.1-51.3-2: $125 credit for a blind or disabled
        # owner of a principal residence, capped at the property tax liability.
        # Modeling notes: modeled as one $125 credit per return (via
        # tax_unit.any) -- IC 6-1.1-51.3-2 has no one-credit-per-property limit,
        # so two blind/disabled co-owning spouses could arguably each claim $125;
        # is_disabled is broader than the SSA substantial-gainful-activity
        # standard the statute references (is_ssi_disabled is closer); the base
        # is total real_estate_taxes rather than principal-residence-only; and
        # each stacked chapter-57 credit caps independently, so combined credits
        # can exceed a small total liability.
        p = parameters(period).gov.states["in"].tax.property.blind_disabled_credit
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        blind = person("is_blind", period)
        disabled = person("is_disabled", period)
        eligible = tax_unit.any((blind | disabled) & head_or_spouse)
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        return eligible * min_(p.amount, property_tax)
