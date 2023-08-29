from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        person = tax_unit.members

        num_exemp = tax_unit("exemptions", period)
        is_disabled = person("is_disabled", period)
        is_spouse = person("is_tax_unit_spouse", period)
        spouse_disabled = tax_unit("spouse_is_disabled", period)
        spouse_aged = tax_unit("aged_spouse", period)

        return where(
            is_disabled,  # If the tax unit is disabled
            where(
                is_spouse,  # If the tax unit is an individual
                where(
                    spouse_disabled,  # If the spouse of the tax unit is disabled
                    p.disability_exemptions.disabled_spouse
                    * num_exemp,  # 14_000
                    where(
                        spouse_aged,  # If the non-disabled spouse is aged
                        p.disability_exemptions.aged_undisabled_spouse
                        * num_exemp,  # 9_288
                        p.disability_exemptions.unaged_undisabled_spouse
                        * num_exemp,  # 8_144
                    ),
                ),
                p.disability_exemptions.individual * num_exemp,  # 7_000
            ),
            p.regular_exemptions * num_exemp,  # 1_144
        )
