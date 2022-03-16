from openfisca_us.model_api import *


class c17000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Medical expense deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/213"
    unit = USD
    documentation = "Sch A: Medical expenses deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        medical = parameters(period).irs.deductions.itemized.medical
        has_aged = (tax_unit("age_head", period) >= 65) | (
            tax_unit("tax_unit_is_joint", period)
            & (tax_unit("age_spouse", period) >= 65)
        )
        medical_floor_ratio = (
            medical.floor.base + has_aged * medical.floor.aged_addition
        )
        medical_floor = medical_floor_ratio * max_(
            tax_unit("c00100", period), 0
        )
        return max_(
            0,
            tax_unit("filer_e17500", period) - medical_floor,
        )


class c18300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "SALT deduction"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/164"
    documentation = "Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        c18400 = max_(tax_unit("filer_e18400", period), 0)
        c18500 = tax_unit("filer_e18500", period)
        salt = parameters(period).irs.deductions.itemized.salt_and_real_estate
        cap = salt.cap[tax_unit("mars", period)]
        return min_(c18400 + c18500, cap)


class c19200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Interest deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/163"
    unit = USD
    documentation = (
        "Sch A: Interest deducted (component of pre-limitation c21060 total)"
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("filer_e19200", period)


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Charitable deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/170"
    unit = USD
    documentation = "Sch A: Charity contributions deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        charity = parameters(period).irs.deductions.itemized.charity
        posagi = tax_unit("posagi", period)
        lim30 = min_(
            charity.ceiling.non_cash * posagi,
            tax_unit("filer_e20100", period),
        )
        c19700 = min_(
            charity.ceiling.all * posagi,
            lim30 + tax_unit("filer_e19800", period),
        )
        return max_(c19700, 0)


class c20500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Casualty deduction"
    reference = "https://www.law.cornell.edu/uscode/text/26/165"
    unit = USD
    documentation = "Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        casualty = parameters(period).irs.deductions.itemized.casualty
        floor = casualty.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_g20500", period) - floor)
        return deduction * (1 - casualty.haircut)


class c20800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Miscellaneous deductions"
    unit = USD
    documentation = "Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)"

    def formula(tax_unit, period, parameters):
        misc = parameters(period).irs.deductions.itemized.misc
        floor = misc.floor * tax_unit("posagi", period)
        deduction = max_(0, tax_unit("filer_e20400", period) - floor)
        return deduction * (1 - misc.haircut)
