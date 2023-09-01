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
        
        head_exemptions = where(
            person("head_is_disabled", period),
            num_exemp * p.disabled,       # head is disabled
            num_exemp * p.base  # regular exemptions
        )

        spouse_exemptions = where(
            person("is_tax_unit_spouse", period),    # the tax unit is an individual
            where(
                person("spouse_is_disabled", period),   # the spouse is disabled
                num_exemp * p.disabled,
                where(
                    person("aged_spouse", period),                 # the spouse is aged
                    (num_exemp + 1) * p.base,
                    num_exemp * p.base
                )
            ),
            0
        )

        return head_exemptions + spouse_exemptions
        







        base_amount = exemptions * base parameter
        head_disabled = where(head_is_disabled, ....)
        spouse_disabled = where(spouse_is_disabled, ....)
        return x + y+ z



        return where(
            head_disabled,  # If the tax unit is disabled
            where(
                spouse_disabled,  # If the tax unit is an individual
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
                p.disabled * num_exemp,  # 7_000
            ),
            p.base * num_exemp,  # 1_144
        )
