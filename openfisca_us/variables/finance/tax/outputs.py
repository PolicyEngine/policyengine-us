from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class TaxInc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # not accurate, for demo
        return max_(
            0,
            tax_unit("earned", period) - tax_unit("standard", period),
        )


class income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # not accurate, for demo
        return tax_unit("TaxInc", period)


class Taxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        income = tax_unit("income", period)
        MARS = tax_unit("MARS", period)
        brackets = parameters(period).tax.income.bracket
        thresholds = (
            [0]
            + [brackets.thresholds[str(i)][MARS] for i in range(1, 7)]
            + [infinity]
        )
        rates = [brackets.rates[str(i)] for i in range(1, 8)]
        bracketed_amounts = [
            amount_between(income, lower, upper)
            for lower, upper in zip(thresholds[:-1], thresholds[1:])
        ]
        bracketed_tax_amounts = [
            rates[i] * bracketed_amounts[i] for i in range(7)
        ]
        tax_amount = sum(bracketed_tax_amounts)
        return tax_amount


class AfterTaxIncome(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR

    def formula(taxunit, period, parameters):
        return taxunit("earned", period) - taxunit("Taxes", period)


# End of placeholder


class sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR

    def formula(person, period, parameters):
        return add(person, period, "e00900", "e02100", "k1bx14")


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    label = u"sey for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(
            tax_unit.members("sey", period)
            * tax_unit.members("is_tax_unit_dependent", period)
        )


class niit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Net Investment Income Tax from Form 8960"""


class combined(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sum of iitax and payrolltax and lumpsum_tax"""


class filer_earned(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(
            tax_unit.members("earned", period)
            * tax_unit.members("is_tax_unit_dependent", period)
        )


class earned(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(person, period, parameters):
        ALD = parameters(period).tax.ALD
        adjustment = (
            (1.0 - ALD.misc.self_emp_tax_adj)
            * ALD.employer_share
            * person("setax", period)
        )
        return max_(0, add(person, period, "e00200", "setax_") - adjustment)


class was_plus_sey(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(person, period, parameters):
        return person("gross_was", period) + max_(
            0,
            person("sey", period)
            * person.tax_unit("sey_frac_for_extra_OASDI", period),
        )


class eitc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Earned Income Credit"""


class rptc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for filing unit"""


class rptc_p(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for taxpayer"""


class rptc_s(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable Payroll Tax Credit for spouse"""


class exact(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class expanded_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Broad income measure that includes benefit_value_total"""
    )


class iitax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total federal individual income tax liability; appears as INCTAX variable in tc CLI minimal output"""


class num(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """2 when MARS is 2 (married filing jointly); otherwise 1"""
    )


class othertaxes(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other taxes: sum of niit, e09700, e09800 and e09900 (included in c09200)"""


class payrolltax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (employee + employer) payroll tax liability; appears as PAYTAX variable in tc CLI minimal output (payrolltax = ptax_was + setax + ptax_amc)"""

    def formula(tax_unit, period):
        return add(tax_unit, period, "ptax_was", "setax", "extra_payrolltax")


class refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total refundable income tax credits"""


class sep(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """2 when MARS is 3 (married filing separately); otherwise 1"""
    )


class filer_sey(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """sey for the tax unit (excluding dependents)"""

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(
            tax_unit.members("sey", period)
            * tax_unit.members("is_tax_unit_dependent", period)
        )


class basic_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        STD = parameters(period).tax.deductions.standard
        MARS = tax_unit("MARS", period)
        MIDR = tax_unit("MIDR", period)

        c15100_if_DSI = max_(
            STD.dependent.additional_earned_income
            + tax_unit("earned", period),
            STD.dependent.amount,
        )
        basic_if_DSI = min_(STD.amount[MARS], c15100_if_DSI)
        basic_if_not_DSI = where(MIDR, 0, STD.amount[MARS])
        basic_stded = where(
            tax_unit("DSI", period), basic_if_DSI, basic_if_not_DSI
        )
        return basic_stded


class aged_blind_extra_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Aged and blind standard deduction"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        STD = parameters(period).tax.deductions.standard
        MARS = tax_unit("MARS", period)
        MARSType = MARS.possible_values
        num_extra_stded = (
            tax_unit("blind_head", period) * 1
            + tax_unit("blind_spouse", period) * 1
            + (tax_unit("age_head", period) >= STD.aged_or_blind.age_threshold)
            * 1
            + (
                (MARS == MARSType.JOINT)
                & (
                    tax_unit("age_spouse", period)
                    >= STD.aged_or_blind.age_threshold
                )
            )
            * 1
        )
        extra_stded = num_extra_stded * STD.aged_or_blind.amount[MARS]
        return extra_stded


class standard(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Standard deduction (zero for itemizers)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Calculate basic standard deduction
        basic_stded = tax_unit("basic_standard_deduction", period)
        charity = parameters(period).tax.deductions.itemized.charity
        MARS = tax_unit("MARS", period)
        MIDR = tax_unit("MIDR", period)
        MARSType = MARS.possible_values

        # Calculate extra standard deduction for aged and blind
        extra_stded = tax_unit("aged_blind_extra_standard_deduction", period)

        # Calculate the total standard deduction
        standard = basic_stded + extra_stded
        standard = where((MARS == MARSType.SEPARATE) & MIDR, 0, standard)
        standard += charity.allow_nonitemizers * min_(
            tax_unit("c19700", period), charity.nonitemizers_max
        )

        return standard


class surtax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class taxbc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Regular tax on regular taxable income before credits"""


class c00100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Adjusted Gross Income (AGI)"""


class c01000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c02500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Social security (OASDI) benefits included in AGI"""


class c02900(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Total of all 'above the line' income adjustments to get AGI"""
    )


class c03260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )

    def formula(tax_unit, period, parameters):
        ALD = parameters(period).tax.ALD
        return (
            (1.0 - ALD.misc.self_emp_tax_adj)
            * ALD.misc.employer_share
            * tax_unit("setax", period)
        )


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Itemized deductions after phase-out (zero for non-itemizers)"""
    )


class c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemptions after phase-out"""


class qbided(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Qualified Business Income (QBI) deduction"""


class c04800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Regular taxable income"""


class c05200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Tax amount from Sch X,Y,X tables"""


class c05700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c05800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total (regular + AMT) income tax liability before credits (equals taxbc plus c09600)"""


class c07100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Total non-refundable credits used to reduce positive tax liability"""


class c07180(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Nonrefundable credit for child and dependent care expenses from Form 2441"""


class CDCC_refund(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Refundable credit for child and dependent care expenses from Form 2441"""


class c07200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Schedule R credit for the elderly and the disabled"""


class c07220(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (adjusted) from Form 8812"""


class c07230(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Education tax credits non-refundable amount from Form 8863 (includes c87668)"""


class c07240(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07260(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07400(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c07600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c08000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c09200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Income tax liability (including othertaxes) after non-refundable credits are used, but before refundable credits are applied"""


class c09600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) liability"""


class c10960(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """American Opportunity Credit refundable amount from Form 8863"""
    )


class c11070(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Child tax credit (refunded) from Form 8812"""


class c17000(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Medical expenses deducted (component of pre-limitation c21060 total)"""


class e17500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Sch A: Medical expenses, capped as a decimal fraction of AGI"""
    )


class c18300(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local taxes plus real estate taxes deducted (component of pre-limitation c21060 total)"""


class e18400_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local income taxes deductible, capped as a decimal fraction of AGI"""


class e18500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: State and local real estate taxes deductible, capped as a decimal fraction of AGI"""


class c19200(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Interest deducted (component of pre-limitation c21060 total)"""


class e19200_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Interest deduction deductible, capped as a decimal fraction of AGI"""


class c19700(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity contributions deducted (component of pre-limitation c21060 total)"""


class e19800_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity cash contributions deductible, capped as a decimal fraction of AGI"""


class e20100_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Charity noncash contributions deductible, capped as a decimal fraction of AGI"""


class c20500(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Net casualty or theft loss deducted (component of pre-limitation c21060 total)"""


class g20500_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Gross casualty or theft loss deductible, capped as a decimal fraction of AGI"""


class c20800(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Net limited miscellaneous deductions deducted (component of pre-limitation c21060 total)"""


class e20400_capped(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Sch A: Gross miscellaneous deductions deductible, capped as a decimal fraction of AGI"""


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Itemized deductions that are phased out"""


class c21060(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Itemized deductions before phase-out (zero for non-itemizers)"""
    )


class c23650(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c59660(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class c62100(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Alternative Minimum Tax (AMT) taxable income"""


class c87668(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """American Opportunity Credit non-refundable amount from Form 8863 (included in c07230)"""


class care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ctc_new(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class odc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Other Dependent Credit"""


class personal_refundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal refundable credit"""


class recovery_rebate_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Recovery Rebate Credit, from American Rescue Plan Act of 2021"""
    )


class personal_nonrefundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal nonrefundable credit"""


class charity_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Credit for charitable giving"""


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks13(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks14(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class dwks19(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class fstax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class invinc_agi_ec(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class invinc_ec_base(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class lumpsum_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Lumpsum (or head) tax; appears as LSTAX variable in tc CLI minimal output"""


class pre_c04600(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Personal exemption before phase-out"""


class codtc_limited(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ptax_amc(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """Additional Medicare Tax from Form 8959 (included in payrolltax)"""
    )


class ptax_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI FICA tax plus self-employment tax (excludes HI FICA so positive ptax_oasdi is less than ptax_was plus setax)"""

    def formula(tax_unit, period):
        return add(
            tax_unit,
            period,
            "filer_ptax_ss_was",
            "filer_setax_ss",
            "extra_payrolltax",
        )


class ptax_was(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Employee + employer OASDI + HI FICA tax"""

    def formula(tax_unit, period, parameters):
        ptax_was = add(
            tax_unit,
            period,
            "filer_ptax_ss_was",
            "filter_ptax_mc_was",
        )
        return ptax_was


class filer_setax(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Self-employment tax for the tax unit (excluding dependents)"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.sum(
            tax_unit.members("setax", period)
            * not_(tax_unit.members("is_tax_unit_dependent", period))
        )


class ymod(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ymod1(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        """search taxcalc/calcfunctions.py for how calculated and used"""
    )


class ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Universal Basic Income benefit for filing unit"""


class taxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit included in AGI"""


class nontaxable_ubi(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = """Amount of UBI benefit excluded from AGI"""
