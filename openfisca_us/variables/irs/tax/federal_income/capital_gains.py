from openfisca_us.model_api import *


class dwks6(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS6"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        dwks2 = tax_unit("filer_e00650", period)
        dwks3 = tax_unit("filer_e58990", period)
        # dwks4 always assumed to be zero
        dwks5 = max_(0, dwks3)
        return max_(0, dwks2 - dwks5)


class dwks9(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS9"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p23250 = tax_unit("filer_p23250", period)
        c23650 = tax_unit("c23650", period)
        dwks7 = min_(p23250, c23650)  # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # dwks9 = max(0., dwks7 - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        e01100 = tax_unit("filer_e01100", period)
        c24510 = where(e01100 > 0, e01100, max_(0, dwks7) + e01100)
        return max_(0, c24510 - min_(0, tax_unit("filer_e58990", period)))


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS10"
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks10_if_gains = add(tax_unit, period, ["dwks6", "dwks9"])
        dwks10_if_no_gains = max_(
            0,
            min_(
                tax_unit("filer_p23250", period),
                tax_unit("c23650", period),
            ),
        ) + tax_unit("filer_e01100", period)
        return where(
            tax_unit("hasqdivltcg", period),
            dwks10_if_gains,
            dwks10_if_no_gains,
        )


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS13"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks1 = tax_unit("c04800", period)
        e24515 = tax_unit("filer_e24515", period)
        dwks11 = e24515 + tax_unit(
            "filer_e24518", period
        )  # Sch D lines 18 and 19, respectively
        dwks9 = tax_unit("dwks9", period)
        dwks12 = min_(dwks9, dwks11)
        dwks10 = tax_unit("dwks10", period)
        return (dwks10 - dwks12) * tax_unit("hasqdivltcg", period)


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS14"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks1 = tax_unit("c04800", period)
        dwks13 = tax_unit("dwks13", period)
        return max_(0, dwks1 - dwks13) * tax_unit("hasqdivltcg", period)


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS14"
    unit = USD
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )

    def formula(tax_unit, period, parameters):
        dwks14 = tax_unit("dwks14", period)
        capital_gains = parameters(period).irs.capital_gains.brackets
        mars = tax_unit("mars", period)
        dwks1 = tax_unit("c04800", period)
        dwks16 = min_(capital_gains.thresholds["1"][mars], dwks1)
        dwks17 = min_(dwks14, dwks16)
        dwks10 = tax_unit("dwks10", period)
        dwks18 = max_(0, dwks1 - dwks10)
        return max_(dwks17, dwks18) * tax_unit("hasqdivltcg", period)
