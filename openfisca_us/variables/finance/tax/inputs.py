from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class DSI(Variable):
    value_type = bool
    entity = TaxUnit
    label = u"Whether claimed as a dependent on another return"
    definition_period = YEAR


class age_head(Variable):
    value_type = int
    entity = TaxUnit
    label = u"Age in years of the taxpayer"
    definition_period = YEAR


class age_spouse(Variable):
    value_type = int
    entity = TaxUnit
    label = u"Age in years of the spouse"
    definition_period = YEAR


class MIDR(Variable):
    value_type = bool
    entity = TaxUnit
    label = u"Whether the separately filing spouse itemizes"
    definition_period = YEAR


class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    label = u"Whether the taxpayer is blind"
    definition_period = YEAR


class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    label = u"Whether the spouse is blind"
    definition_period = YEAR


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Schedule A: charitable contributions deducted"
    definition_period = YEAR


class e00200p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class e00200s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class c03260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class e00900p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class e02100p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class k1bx14p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class e00900s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class e02100ps(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR


class k1bx14s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
