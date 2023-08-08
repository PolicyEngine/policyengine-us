from policyengine_us.model_api import *


class ms_itemized_deductionss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deduction"
    unit = USD
    definition_period = YEAR

    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf"
        "https://advance.lexis.com/documentpage/teaserdocument/?pdmfid=1000516&crid=9f552d68-042d-4ab6-b45d-4b5ec25d1742&config=00JABhZDIzMTViZS04NjcxLTQ1MDItOTllOS03MDg0ZTQxYzU4ZTQKAFBvZENhdGFsb2f8inKxYiqNVSihJeNKRlUp&pddocfullpath=%2fshared%2fdocument%2fstatutes-legislation%2furn%3acontentItem%3a659V-W3G3-CGX8-0009-00008-00&pddocid=urn%3acontentItem%3a659V-W3G3-CGX8-0009-00008-00&pdcontentcomponentid=234190&pdteaserkey=h3&pditab=allpods&ecomp=7s65kkk&earg=sr0&prid=a60fa5e9-9e96-4e4a-88be-5db3d101cc92"
    ) 
    # Variable modeled after Tax Form: Schedule A
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # get the parameters for calcualtions
        agi = tax_unit("adjusted_gross_income", period)
        misc = tax_unit("misc_deduction", period)

        p = parameters(period).gov.irs.deductions.itemized.misc

        # compute itemized deduction maximum less salt
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)

        # calculate maximum miscellanous amount
        misc_deduction = min_(misc, p.floor * agi)

        return itm_deds_less_salt + misc_deduction
