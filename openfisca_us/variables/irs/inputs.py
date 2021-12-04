from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.tax_unit import MARSType


class dsi(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """True if claimed as dependent on another return; otherwise false"""
    )


class eic(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Number of EIC qualifying children (range: 0 to 3)"""

    def formula(tax_unit, period, parameters):
        return tax_unit.max(
            tax_unit.members("is_tax_unit_head", period)
            * tax_unit.members("age", period)
        )


class flpdyr(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Calendar year for which taxes are calculated"""


class mars(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = MARSType
    default_value = MARSType.SINGLE
    definition_period = YEAR
    label = "Marital status for the tax unit"

    def formula(tax_unit, period, parameters):
        has_spouse = tax_unit.max(
            tax_unit.members("is_tax_unit_spouse", period)
            * (tax_unit.members("age", period) > 0)
        )
        return where(has_spouse, MARSType.JOINT, MARSType.SINGLE)


class midr(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """True if separately filing spouse itemizes; otherwise false"""
    )


class recid(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Unique numeric identifier for filing unit; appears as RECID variable in tc CLI minimal output"""


class xtot(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total number of exemptions for filing unit"""


class age_head(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Age in years of taxpayer (i.e. primary adult)"""

    def formula(tax_unit, period, parameters):
        return tax_unit.max(
            tax_unit.members("is_tax_unit_head", period)
            * tax_unit.members("age", period)
        )


class age_spouse(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Age in years of spouse (i.e. secondary adult if present)"""
    )

    def formula(tax_unit, period, parameters):
        return tax_unit.max(
            tax_unit.members("is_tax_unit_spouse", period)
            * tax_unit.members("age", period)
        )


class agi_bin(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Historical AGI category used in data extrapolation"""


class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = """True if taxpayer is blind; otherwise False"""


class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = """1 if spouse is blind; otherwise 0"""


class cmbtp(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Estimate of income on (AMT) Form 6251 but not in AGI"""


class filer_cmbtp(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Income on Form 6251 not in AGI for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("cmbtp", tax_unit, period)


class e00200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Wages, salaries, and tips net of pension contributions"""
    )


class filer_e00200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Wages, salaries, and tips for filing unit (excluding dependents) net of pension contributions (pencon)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00200", tax_unit, period)


class pencon(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Contributions to defined-contribution pension plans"""


class filer_pencon(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Contributions to defined-contribution pension plans for filing unit (excluding dependents)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("pencon", tax_unit, period)


class e00300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Taxable interest income"""


class filer_e00300(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable interest income for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00300", tax_unit, period)


class e00400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Tax-exempt interest income"""


class filer_e00400(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Tax-exempt interest income for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00400", tax_unit, period)


class e00600(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Ordinary dividends included in AGI"""


class filer_e00600(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Ordinary dividends for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00600", tax_unit, period)


class e00650(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Qualified dividends included in ordinary dividends"""


class filer_e00650(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Qualified dividends included in ordinary dividends for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00650", tax_unit, period)


class e00700(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Taxable refunds of state and local income taxes"""


class filer_e00700(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable refunds of state/local taxes for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00700", tax_unit, period)


class e00800(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Alimony received"""


class filer_e00800(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Alimony for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00800", tax_unit, period)


class e00900(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch C business net profit/loss"""


class filer_e00900(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch C business net profit/loss for filing unit (excluding dependents)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e00900", tax_unit, period)


class e01100(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Capital gain distributions not reported on Sch D"""


class filer_e01100(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Capital gains not reported on Sch D for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e01100", tax_unit, period)


class e01200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Other net gain/loss from Form 4797"""


class filer_e01200(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Other net gain/loss for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e01200", tax_unit, period)


class e01400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Taxable IRA distributions"""


class filer_e01400(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Taxable IRA distributions for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e01400", tax_unit, period)


class e01500(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Total pensions and annuities"""


class filer_e01500(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Pensions and annuities for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e01500", tax_unit, period)


class e01700(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Taxable pensions and annuities"""


class filer_e01700(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Taxable pensions and annuities for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e01700", tax_unit, period)


class e02000(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch E total rental, royalty, partnership, S-corporation, etc, income/loss (includes e26270 and e27200)"""


class filer_e02000(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Rentals, royalties etc. for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e02000", tax_unit, period)


class e02100(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Farm net income/loss from Sch F"""


class filer_e02100(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Farm net income/loss for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e02100", tax_unit, period)


class e02300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Unemployment insurance benefits"""


class filer_e02300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Unemployment insurance benefits for filing unit (excluding dependents)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e02300", tax_unit, period)


class e02400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Total social security (OASDI) benefits"""


class filer_e02400(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Social security benefits for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e02400", tax_unit, period)


class e03150(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Total deductible IRA contributions"""


class filer_e03150(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Deductible IRA contributions for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03150", tax_unit, period)


class e03210(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Student loan interest"""


class filer_e03210(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Student loan interest for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03210", tax_unit, period)


class e03220(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Educator expenses"""


class filer_e03220(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Educator expenses for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03220", tax_unit, period)


class e03230(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Tuition and fees from Form 8917"""


class filer_e03230(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Tuition for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03230", tax_unit, period)


class e03240(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Domestic production activities from Form 8903"""


class filer_e03240(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Domestic production activities for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03240", tax_unit, period)


class e03270(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Self-employed health insurance deduction"""


class filer_e03270(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Self-employed health insurance for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03270", tax_unit, period)


class e03290(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Health savings account deduction from Form 8889"""


class filer_e03290(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Health savings account deduction for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03290", tax_unit, period)


class e03300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Contributions to SEP, SIMPLE and qualified plans"""


class filer_e03300(Variable):
    value_type = float
    entity = TaxUnit
    label = u"SEP, SIMPLE, etc. contributions for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03300", tax_unit, period)


class e03400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Penalty on early withdrawal of savings"""


class filer_e03400(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Early savings withdrawal penalty for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03400", tax_unit, period)


class e03500(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Alimony paid"""


class filer_e03500(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Alimony paid for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e03500", tax_unit, period)


class e07240(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Retirement savings contributions credit from Form 8880"""
    )


class e07260(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Residential energy credit from Form 5695"""


class e07300(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Foreign tax credit from Form 1116"""


class filer_e07300(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Foreign tax credit (Form 1116) for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e07300", tax_unit, period)


class e07400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """General business credit from Form 3800"""


class e07600(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Prior year minimum tax credit from Form 8801"""


class e09700(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Recapture of Investment Credit"""


class e09800(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Unreported payroll taxes from Form 4137 or 8919"""


class e09900(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Penalty tax on qualified retirement plans"""


class e11200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Excess payroll (FICA/RRTA) tax withheld"""


class e17500(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable medical and dental expenses.  WARNING: this variable is zero below the floor in PUF data."""


class filer_e17500(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized medical and dental expenses for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e17500", tax_unit, period)


class e18400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable state and local income/sales taxes"""


class filer_e18400(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized SALT for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e18400", tax_unit, period)


class e18500(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable real-estate taxes paid"""


class filer_e18500(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized real estate for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e18500", tax_unit, period)


class e19200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable interest paid"""


class filer_e19200(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemizable interest paid for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e19200", tax_unit, period)


class e19800(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable charitable giving: cash/check contributions.  WARNING: this variable is already capped in PUF data."""


class filer_e19800(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized charity for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e19800", tax_unit, period)


class e20100(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable charitable giving: other than cash/check contributions.  WARNING: this variable is already capped in PUF data."""


class filer_e20100(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Itemized non-cash charity for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e20100", tax_unit, period)


class e20400(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable miscellaneous deductions.  WARNING: this variable is zero below the floor in PUF data."""


class filer_e20400(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized misc. for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e20400", tax_unit, period)


class g20500(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Itemizable gross (before 10% AGI disregard) casualty or theft loss"""


class filer_g20500(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Itemized casualty loss for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("g20500", tax_unit, period)


class e24515(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch D: Un-Recaptured Section 1250 Gain"""


class e24518(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch D: 28% Rate Gain or Loss"""


class e26270(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch E: Combined partnership and S-corporation net income/loss (includes k1bx14p and k1bx14s amounts and is included in e02000)"""


class filer_e26270(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Label for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e26270", tax_unit, period)


class e27200(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Sch E: Farm rent net income or loss (included in e02000)"""
    )


class filer_e27200(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Label for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e27200", tax_unit, period)


class e32800(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Child/dependent-care expenses for qualifying persons from Form 2441"""


class filer_e32800(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Child/dependent-care expenses for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("e32800", tax_unit, period)


class e58990(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Investment income elected amount from Form 4952"""


class e62900(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Alternative Minimum Tax foreign tax credit from Form 6251"""
    )


class e87530(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Adjusted qualified lifetime learning expenses for all students"""
    )


class elderly_dependents(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """number of dependents age 65+ in filing unit excluding taxpayer and spouse"""


class f2441(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """number of child/dependent-care qualifying persons"""


class f6251(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """True if Form 6251 (AMT) attached to return; otherwise false"""
    )


class a_lineno(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """CPS line number for the person record of the head of the tax filing unit (not used in tax-calculation logic)"""


class ffpos(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """CPS family identifier within household (not used in tax-calculation logic)"""


class fips(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """FIPS state code (not used in tax-calculation logic)"""


class h_seq(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """CPS household sequence number (not used in tax-calculation logic)"""
    )


class data_source(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = """True if unit is created primarily from IRS-SOI PUF data; false if created primarily from CPS data (not used in tax-calculation logic)"""


class k1bx14(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """Partner self-employment earnings/loss (included in e26270 total)"""
    )


class filer_k1bx14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Partner self-employment earnings/loss for tax unit (excluding dependents) (included in e26270 total)"""

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("k1bx14", tax_unit, period)


class mcaid_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed Medicaid benefits expressed as the actuarial value of Medicaid health insurance"""


class mcare_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed Medicare benefits expressed as the actuarial value of Medicare health insurance"""


class n24(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Number of children who are Child-Tax-Credit eligible, one condition for which is being under age 17"""


class nu06(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Number of dependents under 6 years old"""


class nu13(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Number of dependents under 13 years old"""


class nu18(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Number of people under 18 years old in the filing unit"""
    )


class n1820(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Number of people age 18-20 years old in the filing unit"""
    )


class n21(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Number of people 21 years old or older in the filing unit"""
    )


class other_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Non-imputed benefits"""


class p08000(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Other tax credits (but not including Sch R credit)"""


class p22250(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch D: Net short-term capital gains/losses"""


class filer_p22250(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Net short-term capital gains for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("p22250", tax_unit, period)


class p23250(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = """Sch D: Net long-term capital gains/losses"""


class filer_p23250(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        u"Net long-term capital gains for the tax unit (excluding dependents)"
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum("p23250", tax_unit, period)


class e87521(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total tentative AmOppCredit amount for all students"""


class s006(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Filing unit sampling weight; appears as WEIGHT variable in tc CLI minimal output"""


class snap_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed SNAP benefits"""


class housing_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed housing benefits"""


class ssi_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed SSI benefits"""


class tanf_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed TANF benefits"""


class vet_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed Veteran's benefits"""


class wic_ben(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Imputed WIC benefits"""


class pt_sstb_income(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Whether business income is from a specified service trade or business (SSTB), rather than from a qualified trade or business"""


class pt_binc_w2_wages(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Filing unit's share of total W-2 wages paid by the pass-through business"""


class pt_ubia_property(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Filing unit's share of total business property owned by the pass-through business"""
