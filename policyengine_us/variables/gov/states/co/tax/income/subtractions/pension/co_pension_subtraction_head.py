from policyengine_us.model_api import *


class co_pension_subtraction_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado pension and annuity subtraction for head"
    defined_for = StateCode.CO
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=d0c36b4d-118b-4999-860c-acf7e2abc639&nodeid=ABPAACAACAABAACAAF&nodepath=%2FROOT%2FABP%2FABPAAC%2FABPAACAAC%2FABPAACAACAAB%2FABPAACAACAABAAC%2FABPAACAACAABAACAAF&level=6&haschildren=&populated=false&title=39-22-104.+Income+tax+imposed+on+individuals%2C+estates%2C+and+trusts+-+single+rate+-+report+-+legislative+declaration+-+definitions+-+repeal.&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A683G-JJ73-CGX8-04HR-00008-00&ecomp=7gf59kk&prid=a3e24fb9-619e-4e55-9f4a-0513857dd3ef"
        # C.R.S. 39-22-104(4)(f)(III)
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        person = tax_unit.members
        taxable_pension_income = person("taxable_pension_income", period)
        co_pension_survivors = person("co_pension_survivors", period)
        co_social_security_subtraction_head = tax_unit(
            "co_social_security_subtraction_head", period
        )
        age_head = tax_unit("age_head", period)
        younger_condition = age_head < p.younger.age
        older_condition = age_head >= p.older.age
        co_pension_survivors = tax_unit.max(
            co_pension_survivors * person("is_tax_unit_head", period)
        )
        head_tpi = tax_unit.max(
            taxable_pension_income * person("is_tax_unit_head", period)
        )
        # subtract $20,000 minus any amount entered on line 3(co_social_security_subtraction_head), or co_pension_survivors, whichever is smaller.
        # if the amount on line 3 of this form is greater than $20,000, you may not claim any subtraction.
        younger_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_head, 0
        )
        younger_head_output = min_(younger_allowable, co_pension_survivors)
        # subtract $24,000 minus any amount entered on line 3(co_social_security_subtraction_head), or taxable_pension_income, whichever is smaller.
        # if the amount on line 3 of this form is greater than $24,000, you may not claim any subtraction.
        older_allowable = max_(
            p.older.max_amount - co_social_security_subtraction_head, 0
        )
        older_head_output = min_(older_allowable, head_tpi)
        # subtract $20,000 minus any amount entered on line 3(co_social_security_subtraction_head), or taxable_pension_income, whichever is smaller.
        # if the amount on line 3 of this form is greater than $20,000, you may not claim any subtraction.
        intermediate_allowable = max_(
            p.younger.max_amount - co_social_security_subtraction_head, 0
        )
        intermediate_head_output = min_(intermediate_allowable, head_tpi)
        return where(
            younger_condition,
            younger_head_output,
            where(
                older_condition,
                older_head_output,
                intermediate_head_output,
            ),
        )
