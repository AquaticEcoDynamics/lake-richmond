from typing import Union, List
from glmpy.nml.nml import BLOCK_REGISTER, NMLParam, NMLBlock, NML


@BLOCK_REGISTER.register()
class ModelsBlock(NMLBlock):
    block_name = "aed_models"

    def __init__(
        self,
        models: Union[List[str], None] = None,
    ):
        """ """
        super().__init__()
        self.params["models"] = NMLParam("models", str, models, is_list=True)

        self.strict = True

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class OxygenBlock(NMLBlock):
    block_name = "aed_oxygen"

    def __init__(
        self,
        oxy_initial: Union[float, None] = None,
        fsed_oxy: Union[float, None] = None,
        ksed_oxy: Union[float, None] = None,
        theta_sed_oxy: Union[float, None] = None,
        fsed_oxy_variable: Union[str, None] = None,
        oxy_min: Union[float, None] = None,
        oxy_max: Union[float, None] = None,
    ):
        super().__init__()
        self.params["oxy_initial"] = NMLParam(
            "oxy_initial", float, oxy_initial, units="mmol m^{-3}"
        )
        self.params["fsed_oxy"] = NMLParam(
            "fsed_oxy", float, fsed_oxy, units="mmol m^{-2} day^{-1}"
        )
        self.params["ksed_oxy"] = NMLParam(
            "ksed_oxy", float, ksed_oxy, units="mmol m^{-3}"
        )
        self.params["theta_sed_oxy"] = NMLParam(
            "theta_sed_oxy",
            float,
            theta_sed_oxy,
        )
        self.params["fsed_oxy_variable"] = NMLParam(
            "fsed_oxy_variable",
            str,
            fsed_oxy_variable,
        )
        self.params["oxy_min"] = NMLParam(
            "oxy_min", float, oxy_min, units="mmol m^{-3}"
        )
        self.params["oxy_max"] = NMLParam(
            "oxy_max", float, oxy_max, units="mmol m^{-3}"
        )

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class SedFluxBlock(NMLBlock):
    block_name = "aed_sedflux"

    def __init__(self, sedflux_model: Union[str, None] = None):
        super().__init__()
        self.params["sedflux_model"] = NMLParam(
            "sedflux_model",
            str,
            sedflux_model,
            val_switch=["Constant", "Constant2d", "Dynamic", "Dynamic2d"],
            val_required=True,
        )

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class SedConst2DBlock(NMLBlock):
    block_name = "aed_sed_const2d"

    def __init__(
        self,
        n_zones: Union[int, None] = None,
        active_zones: Union[List[int], None] = None,
        fsed_oxy: Union[List[float], None] = None,
        fsed_amm: Union[List[float], None] = None,
        fsed_nit: Union[List[float], None] = None,
        fsed_frp: Union[List[float], None] = None,
    ):
        super().__init__()
        self.params["n_zones"] = NMLParam("n_zones", int, n_zones)
        self.params["active_zones"] = NMLParam(
            "active_zones", int, active_zones, is_list=True
        )
        self.params["fsed_oxy"] = NMLParam(
            "fsed_oxy", float, fsed_oxy, is_list=True
        )
        self.params["fsed_amm"] = NMLParam(
            "fsed_amm", float, fsed_amm, is_list=True
        )
        self.params["fsed_nit"] = NMLParam(
            "fsed_nit", float, fsed_nit, is_list=True
        )
        self.params["fsed_frp"] = NMLParam(
            "fsed_frp", float, fsed_frp, is_list=True
        )

    def validate(self):
        self.params.validate()
        self.val_list_len_params("n_zones", "active_zones")
        self.val_list_len_params("n_zones", "fsed_oxy")
        self.val_list_len_params("n_zones", "fsed_oxy")
        self.val_list_len_params("n_zones", "fsed_amm")
        self.val_list_len_params("n_zones", "fsed_nit")
        self.val_list_len_params("n_zones", "fsed_frp")


@BLOCK_REGISTER.register()
class SilicaBlock(NMLBlock):
    block_name = "aed_silica"

    def __init__(
        self,
        rsi_initial: Union[float, None] = None,
        rsi_min: Union[float, None] = None,
        rsi_max: Union[float, None] = None,
        fsed_rsi: Union[float, None] = None,
        ksed_rsi: Union[float, None] = None,
        theta_sed_rsi: Union[float, None] = None,
        fsed_rsi_variable: Union[str, None] = None,
        silica_reactant_variable: Union[str, None] = None,
    ):
        super().__init__()
        self.params["rsi_initial"] = NMLParam(
            "rsi_initial", float, rsi_initial, units="mmol Si m^{-3}"
        )
        self.params["rsi_min"] = NMLParam(
            "rsi_min", float, rsi_min, units="mmol Si m^{-3}"
        )
        self.params["rsi_max"] = NMLParam(
            "rsi_max", float, rsi_max, units="mmol Si m^{-3}"
        )
        self.params["fsed_rsi"] = NMLParam(
            "fsed_rsi", float, fsed_rsi, units="mmol Si m^{-2} d^{-1}"
        )
        self.params["ksed_rsi"] = NMLParam(
            "ksed_rsi", float, ksed_rsi, units="mmol Si m^{-3}"
        )
        self.params["theta_sed_rsi"] = NMLParam(
            "theta_sed_rsi", float, theta_sed_rsi, units="mmol Si m^{-3}"
        )
        self.params["fsed_rsi_variable"] = NMLParam(
            "fsed_rsi_variable", str, fsed_rsi_variable
        )
        self.params["silica_reactant_variable"] = NMLParam(
            "silica_reactant_variable", str, silica_reactant_variable
        )

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class NitrogenBlock(NMLBlock):
    block_name = "aed_nitrogen"

    def __init__(
        self,
        amm_initial: Union[float, None] = None,
        nit_initial: Union[float, None] = None,
        n2o_initial: Union[float, None] = None,
        no2_initial: Union[float, None] = None,
        rnitrif: Union[float, None] = None,
        knitrif: Union[float, None] = None,
        theta_nitrif: Union[float, None] = None,
        nitrif_reactant_variable: Union[str, None] = None,
        nitrif_ph_variable: Union[str, None] = None,
        simnitrfph: Union[bool, None] = None,
        rnh4o2: Union[float, None] = None,
        rno2o2: Union[float, None] = None,
        simn2o: Union[int, None] = None,
        rn2o: Union[float, None] = None,
        kpart_ammox: Union[float, None] = None,
        kin_deamm: Union[float, None] = None,
        atm_n2o: Union[float, None] = None,
        n2o_piston_model: Union[int, None] = None,
        rnh4no2: Union[float, None] = None,
        kanammox: Union[float, None] = None,
        kanmx_nit: Union[float, None] = None,
        kanmx_amm: Union[float, None] = None,
        rdenit: Union[float, None] = None,
        kdenit: Union[float, None] = None,
        theta_denit: Union[float, None] = None,
        rdnra: Union[float, None] = None,
        kdnra_oxy: Union[float, None] = None,
        simdrydeposition: Union[bool, None] = None,
        atm_din_dd: Union[float, None] = None,
        simwetdeposition: Union[bool, None] = None,
        atm_din_conc: Union[float, None] = None,
        ksed_amm: Union[float, None] = None,
        ksed_nit: Union[float, None] = None,
        fsed_n2o: Union[float, None] = None,
        ksed_n2o: Union[float, None] = None,
        theta_sed_amm: Union[float, None] = None,
        theta_sed_nit: Union[float, None] = None,
        fsed_amm: Union[float, None] = None,
        fsed_nit: Union[float, None] = None,
        fsed_amm_variable: Union[str, None] = None,
        fsed_nit_variable: Union[str, None] = None,
    ):
        super().__init__()
        self.params["amm_initial"] = NMLParam(
            "amm_initial", float, amm_initial
        )
        self.params["nit_initial"] = NMLParam(
            "nit_initial", float, nit_initial
        )
        self.params["n2o_initial"] = NMLParam(
            "n2o_initial", float, n2o_initial
        )
        self.params["no2_initial"] = NMLParam(
            "no2_initial", float, no2_initial
        )
        self.params["rnitrif"] = NMLParam(
            "rnitrif", float, rnitrif, units="day^{-1}"
        )
        self.params["knitrif"] = NMLParam("knitrif", float, knitrif)
        self.params["theta_nitrif"] = NMLParam(
            "theta_nitrif", float, theta_nitrif
        )
        self.params["nitrif_reactant_variable"] = NMLParam(
            "nitrif_reactant_variable", str, nitrif_reactant_variable
        )
        self.params["nitrif_ph_variable"] = NMLParam(
            "nitrif_ph_variable", str, nitrif_ph_variable
        )
        self.params["simnitrfph"] = NMLParam("simnitrfph", bool, simnitrfph)
        self.params["rnh4o2"] = NMLParam(
            "rnh4o2", float, rnh4o2, units="mmol^{-1} m^{3} s^{-1}"
        )
        self.params["rno2o2"] = NMLParam(
            "rno2o2", float, rno2o2, units="mmol^{-1} m^{3} s^{-1}"
        )
        self.params["simn2o"] = NMLParam("simn2o", int, simn2o)
        self.params["rn2o"] = NMLParam("rn2o", float, rn2o, units="s^{-1}")
        self.params["kpart_ammox"] = NMLParam(
            "kpart_ammox", float, kpart_ammox, units="mmol m^{-3}"
        )
        self.params["kin_deamm"] = NMLParam(
            "kin_deamm", float, kin_deamm, units="mmol m^{-3}"
        )
        self.params["atm_n2o"] = NMLParam(
            "atm_n2o", float, atm_n2o, units="mmol m^{-3}"
        )
        self.params["n2o_piston_model"] = NMLParam(
            "n2o_piston_model", int, n2o_piston_model
        )
        self.params["rnh4no2"] = NMLParam(
            "rnh4no2", float, rnh4no2, units="mmol^{-1} m^{3} s^{-1}"
        )
        self.params["kanammox"] = NMLParam("kanammox", float, kanammox)
        self.params["kanmx_nit"] = NMLParam("kanmx_nit", float, kanmx_nit)
        self.params["kanmx_amm"] = NMLParam("kanmx_amm", float, kanmx_amm)
        self.params["rdenit"] = NMLParam("rdenit", float, rdenit)
        self.params["kdenit"] = NMLParam(
            "kdenit", float, kdenit, units="mmol m^{-3}"
        )
        self.params["theta_denit"] = NMLParam(
            "theta_denit", float, theta_denit
        )
        self.params["rdnra"] = NMLParam("rdnra", float, rdnra)
        self.params["kdnra_oxy"] = NMLParam("kdnra_oxy", float, kdnra_oxy)
        self.params["simdrydeposition"] = NMLParam(
            "simdrydeposition", bool, simdrydeposition
        )
        self.params["atm_din_dd"] = NMLParam(
            "atm_din_dd", float, atm_din_dd, units="mmol m^{-2} d^{-1}"
        )
        self.params["simwetdeposition"] = NMLParam(
            "simwetdeposition", bool, simwetdeposition
        )
        self.params["atm_din_conc"] = NMLParam(
            "atm_din_conc", float, atm_din_conc, units="mmol m^{-3}"
        )
        self.params["ksed_amm"] = NMLParam(
            "ksed_amm", float, ksed_amm, units="mmol m^{-2} d^{-1}"
        )
        self.params["ksed_nit"] = NMLParam(
            "ksed_nit", float, ksed_nit, units="mmol m^{-2} d^{-1}"
        )
        self.params["fsed_n2o"] = NMLParam(
            "fsed_n2o", float, fsed_n2o, units="mmol m^{-2} y^{-1}"
        )
        self.params["ksed_n2o"] = NMLParam(
            "ksed_n2o", float, ksed_n2o, units="mmol m^{-2} y^{-1}"
        )
        self.params["theta_sed_amm"] = NMLParam(
            "theta_sed_amm", float, theta_sed_amm
        )
        self.params["theta_sed_nit"] = NMLParam(
            "theta_sed_nit", float, theta_sed_nit
        )
        self.params["fsed_amm"] = NMLParam("fsed_amm", float, fsed_amm)
        self.params["fsed_nit"] = NMLParam("fsed_nit", float, fsed_nit)
        self.params["fsed_amm_variable"] = NMLParam(
            "fsed_amm_variable", str, fsed_amm_variable
        )
        self.params["fsed_nit_variable"] = NMLParam(
            "fsed_nit_variable", str, fsed_nit_variable
        )

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class PhosphorusBlock(NMLBlock):
    block_name = "aed_phosphorus"

    def __init__(
        self,
        frp_initial: Union[float, None] = None,
        frp_min: Union[float, None] = None,
        frp_max: Union[float, None] = None,
        fsed_frp: Union[float, None] = None,
        ksed_frp: Union[float, None] = None,
        theta_sed_frp: Union[float, None] = None,
        phosphorus_reactant_variable: Union[str, None] = None,
        fsed_frp_variable: Union[str, None] = None,
        simpo4adsorption: Union[bool, None] = None,
        ads_use_external_tss: Union[bool, None] = None,
        po4sorption_target_variable: Union[str, None] = None,
        po4adsorptionmodel: Union[int, None] = None,
        kpo4p: Union[float, None] = None,
        kadsratio: Union[float, None] = None,
        qmax: Union[float, None] = None,
        w_po4ads: Union[float, None] = None,
        ads_use_ph: Union[bool, None] = None,
        ph_variable: Union[str, None] = None,
        simdrydeposition: Union[bool, None] = None,
        atm_pip_dd: Union[float, None] = None,
        simwetdeposition: Union[bool, None] = None,
        atm_frp_conc: Union[float, None] = None,
    ):
        super().__init__()
        self.params["frp_initial"] = NMLParam(
            "frp_initial", float, frp_initial, units="mmol P m^{-3}"
        )
        self.params["frp_min"] = NMLParam(
            "frp_min", float, frp_min, units="mmol P m^{-3}"
        )
        self.params["frp_max"] = NMLParam(
            "frp_max", float, frp_max, units="mmol P m^{-3}"
        )
        self.params["fsed_frp"] = NMLParam(
            "fsed_frp", float, fsed_frp, units="mmol P m^{-3} d^{-1}"
        )
        self.params["ksed_frp"] = NMLParam(
            "ksed_frp", float, ksed_frp, units="mmol O_{2} m^{-3}"
        )
        self.params["theta_sed_frp"] = NMLParam(
            "theta_sed_frp", float, theta_sed_frp
        )
        self.params["phosphorus_reactant_variable"] = NMLParam(
            "phosphorus_reactant_variable", str, phosphorus_reactant_variable
        )
        self.params["fsed_frp_variable"] = NMLParam(
            "fsed_frp_variable", str, fsed_frp_variable
        )
        self.params["simpo4adsorption"] = NMLParam(
            "simpo4adsorption", bool, simpo4adsorption
        )
        self.params["ads_use_external_tss"] = NMLParam(
            "ads_use_external_tss", bool, ads_use_external_tss
        )
        self.params["po4sorption_target_variable"] = NMLParam(
            "po4sorption_target_variable", str, po4sorption_target_variable
        )
        self.params["po4adsorptionmodel"] = NMLParam(
            "po4adsorptionmodel", int, po4adsorptionmodel
        )
        self.params["kpo4p"] = NMLParam(
            "kpo4p", float, kpo4p, units="m^{3} g^{-1}"
        )
        self.params["kadsratio"] = NMLParam(
            "kadsratio", float, kadsratio, units="l mg^{-1}"
        )
        self.params["qmax"] = NMLParam(
            "qmax", float, qmax, units="mg mgSS^{-1}"
        )
        self.params["w_po4ads"] = NMLParam(
            "w_po4ads", float, w_po4ads, units="m d^{-1}"
        )
        self.params["ads_use_ph"] = NMLParam("ads_use_ph", bool, ads_use_ph)
        self.params["ph_variable"] = NMLParam("ph_variable", str, ph_variable)
        self.params["simdrydeposition"] = NMLParam(
            "simdrydeposition", bool, simdrydeposition
        )
        self.params["atm_pip_dd"] = NMLParam(
            "atm_pip_dd", float, atm_pip_dd, units="mmol P m^{-2} d^{-1}"
        )
        self.params["simwetdeposition"] = NMLParam(
            "simwetdeposition", bool, simwetdeposition
        )
        self.params["atm_frp_conc"] = NMLParam(
            "atm_frp_conc", float, atm_frp_conc, units="mmol P m^{-3}"
        )

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class OrganicMatterBlock(NMLBlock):
    block_name = "aed_organic_matter"

    def __init__(
        self,
        poc_initial: Union[float, None] = None,
        doc_initial: Union[float, None] = None,
        pon_initial: Union[float, None] = None,
        don_initial: Union[float, None] = None,
        pop_initial: Union[float, None] = None,
        dop_initial: Union[float, None] = None,
        docr_initial: Union[float, None] = None,
        donr_initial: Union[float, None] = None,
        dopr_initial: Union[float, None] = None,
        cpom_initial: Union[float, None] = None,
        rpoc_hydrol: Union[float, None] = None,
        rpon_hydrol: Union[float, None] = None,
        rpop_hydrol: Union[float, None] = None,
        theta_hydrol: Union[float, None] = None,
        kpom_hydrol: Union[float, None] = None,
        rdom_minerl: Union[float, None] = None,
        theta_minerl: Union[float, None] = None,
        kdom_minerl: Union[float, None] = None,
        simdenitrification: Union[int, None] = None,
        f_an: Union[float, None] = None,
        k_nit: Union[float, None] = None,
        dom_miner_oxy_reactant_var: Union[str, None] = None,
        dom_miner_nit_reactant_var: Union[str, None] = None,
        dom_miner_no2_reactant_var: Union[str, None] = None,
        dom_miner_n2o_reactant_var: Union[str, None] = None,
        dom_miner_fe3_reactant_var: Union[str, None] = None,
        dom_miner_so4_reactant_var: Union[str, None] = None,
        dom_miner_ch4_reactant_var: Union[str, None] = None,
        doc_miner_product_variable: Union[str, None] = None,
        don_miner_product_variable: Union[str, None] = None,
        dop_miner_product_variable: Union[str, None] = None,
        simrpools: Union[bool, None] = None,
        rdomr_minerl: Union[float, None] = None,
        rcpom_bdown: Union[float, None] = None,
        x_cpom_n: Union[float, None] = None,
        x_cpom_p: Union[float, None] = None,
        kedom: Union[float, None] = None,
        kepom: Union[float, None] = None,
        kedomr: Union[float, None] = None,
        kecpom: Union[float, None] = None,
        simphotolysis: Union[bool, None] = None,
        photo_c: Union[float, None] = None,
        settling: Union[int, None] = None,
        w_pom: Union[float, None] = None,
        d_pom: Union[float, None] = None,
        rho_pom: Union[float, None] = None,
        w_cpom: Union[float, None] = None,
        d_cpom: Union[float, None] = None,
        rho_cpom: Union[float, None] = None,
        resuspension: Union[int, None] = None,
        resus_link: Union[str, None] = None,
        sedimentomfrac: Union[float, None] = None,
        xsc: Union[float, None] = None,
        xsn: Union[float, None] = None,
        xsp: Union[float, None] = None,
        fsed_doc: Union[float, None] = None,
        fsed_don: Union[float, None] = None,
        fsed_dop: Union[float, None] = None,
        ksed_dom: Union[float, None] = None,
        theta_sed_dom: Union[float, None] = None,
        fsed_doc_variable: Union[str, None] = None,
        fsed_don_variable: Union[str, None] = None,
        fsed_dop_variable: Union[str, None] = None,
        diag_level: Union[int, None] = None,
    ):
        super().__init__()
        self.params["poc_initial"] = NMLParam(
            "poc_initial", float, poc_initial, units="mmol C m^{-3}"
        )
        self.params["doc_initial"] = NMLParam(
            "doc_initial", float, doc_initial, units="mmol C m^{-3}"
        )
        self.params["pon_initial"] = NMLParam(
            "pon_initial", float, pon_initial, units="mmol N m^{-3}"
        )
        self.params["don_initial"] = NMLParam(
            "don_initial", float, don_initial, units="mmol C m^{-3}"
        )
        self.params["pop_initial"] = NMLParam(
            "pop_initial", float, pop_initial, units="mmol P m^{-3}"
        )
        self.params["dop_initial"] = NMLParam(
            "dop_initial", float, dop_initial, units="mmol P m^{-3}"
        )
        self.params["docr_initial"] = NMLParam(
            "docr_initial", float, docr_initial
        )
        self.params["donr_initial"] = NMLParam(
            "donr_initial", float, donr_initial
        )
        self.params["dopr_initial"] = NMLParam(
            "dopr_initial", float, dopr_initial
        )
        self.params["cpom_initial"] = NMLParam(
            "cpom_initial", float, cpom_initial, units="mmol C m^{-3}"
        )
        self.params["rpoc_hydrol"] = NMLParam(
            "rpoc_hydrol", float, rpoc_hydrol, units="d^{-1}"
        )
        self.params["rpon_hydrol"] = NMLParam(
            "rpon_hydrol", float, rpon_hydrol, units="d^{-1}"
        )
        self.params["rpop_hydrol"] = NMLParam(
            "rpop_hydrol", float, rpop_hydrol, units="d^{-1}"
        )
        self.params["theta_hydrol"] = NMLParam(
            "theta_hydrol", float, theta_hydrol
        )
        self.params["kpom_hydrol"] = NMLParam(
            "kpom_hydrol", float, kpom_hydrol, units="mmol O_{2} m^{-3}"
        )
        self.params["rdom_minerl"] = NMLParam(
            "rdom_minerl", float, rdom_minerl, units="d^{-1}"
        )
        self.params["theta_minerl"] = NMLParam(
            "theta_minerl", float, theta_minerl
        )
        self.params["kdom_minerl"] = NMLParam(
            "kdom_minerl", float, kdom_minerl, units="mmol O_{2} m^{-3}"
        )
        self.params["simdenitrification"] = NMLParam(
            "simdenitrification", int, simdenitrification
        )
        self.params["f_an"] = NMLParam("f_an", float, f_an)
        self.params["k_nit"] = NMLParam(
            "k_nit", float, k_nit, units="mmol N m^{-3}"
        )
        self.params["dom_miner_oxy_reactant_var"] = NMLParam(
            "dom_miner_oxy_reactant_var", str, dom_miner_oxy_reactant_var
        )
        self.params["dom_miner_nit_reactant_var"] = NMLParam(
            "dom_miner_nit_reactant_var", str, dom_miner_nit_reactant_var
        )
        self.params["dom_miner_no2_reactant_var"] = NMLParam(
            "dom_miner_no2_reactant_var", str, dom_miner_no2_reactant_var
        )
        self.params["dom_miner_n2o_reactant_var"] = NMLParam(
            "dom_miner_n2o_reactant_var", str, dom_miner_n2o_reactant_var
        )
        self.params["dom_miner_fe3_reactant_var"] = NMLParam(
            "dom_miner_fe3_reactant_var", str, dom_miner_fe3_reactant_var
        )
        self.params["dom_miner_so4_reactant_var"] = NMLParam(
            "dom_miner_so4_reactant_var", str, dom_miner_so4_reactant_var
        )
        self.params["dom_miner_ch4_reactant_var"] = NMLParam(
            "dom_miner_ch4_reactant_var", str, dom_miner_ch4_reactant_var
        )
        self.params["doc_miner_product_variable"] = NMLParam(
            "doc_miner_product_variable", str, doc_miner_product_variable
        )
        self.params["don_miner_product_variable"] = NMLParam(
            "don_miner_product_variable", str, don_miner_product_variable
        )
        self.params["dop_miner_product_variable"] = NMLParam(
            "dop_miner_product_variable", str, dop_miner_product_variable
        )
        self.params["simrpools"] = NMLParam("simrpools", bool, simrpools)
        self.params["rdomr_minerl"] = NMLParam(
            "rdomr_minerl", float, rdomr_minerl, units="d^{-1}"
        )
        self.params["rcpom_bdown"] = NMLParam(
            "rcpom_bdown", float, rcpom_bdown, units="d^{-1}"
        )
        self.params["x_cpom_n"] = NMLParam(
            "x_cpom_n", float, x_cpom_n, units="(mmol N) (mmol C^{-1})"
        )
        self.params["x_cpom_p"] = NMLParam(
            "x_cpom_p", float, x_cpom_p, units="(mmol P) (mmol C^{-1})"
        )
        self.params["kedom"] = NMLParam(
            "kedom", float, kedom, units="m^{-1} ((mmol C) m^{-2})^{-1}"
        )
        self.params["kepom"] = NMLParam(
            "kepom", float, kepom, units="m^{-1} ((mmol C) m^{-2})^{-1}"
        )
        self.params["kedomr"] = NMLParam(
            "kedomr", float, kedomr, units="m^{-1} ((mmol C) m^{-2})^{-1}"
        )
        self.params["kecpom"] = NMLParam(
            "kecpom", float, kecpom, units="m^{-1} ((mmol C) m^{-2})^{-1}"
        )
        self.params["simphotolysis"] = NMLParam(
            "simphotolysis", bool, simphotolysis
        )
        self.params["photo_c"] = NMLParam("photo_c", float, photo_c)
        self.params["settling"] = NMLParam("settling", int, settling)
        self.params["w_pom"] = NMLParam(
            "w_pom", float, w_pom, units="m d^{-1}"
        )
        self.params["d_pom"] = NMLParam("d_pom", float, d_pom, units="m")
        self.params["rho_pom"] = NMLParam(
            "rho_pom", float, rho_pom, units="kg m^{-3}"
        )
        self.params["w_cpom"] = NMLParam(
            "w_cpom", float, w_cpom, units="m d^{-1}"
        )
        self.params["d_cpom"] = NMLParam("d_cpom", float, d_cpom, units="m")
        self.params["rho_cpom"] = NMLParam(
            "rho_cpom", float, rho_cpom, units="kg d^{-3}"
        )
        self.params["resuspension"] = NMLParam(
            "resuspension", int, resuspension
        )
        self.params["resus_link"] = NMLParam("resus_link", str, resus_link)
        self.params["sedimentomfrac"] = NMLParam(
            "sedimentomfrac",
            float,
            sedimentomfrac,
            units="(g OM) (g sediment)^{-1}",
        )
        self.params["xsc"] = NMLParam(
            "xsc", float, xsc, units="(mmol C) (g OM)^{-1}"
        )
        self.params["xsn"] = NMLParam(
            "xsn", float, xsn, units="(mmol N) (g OM)^{-1}"
        )
        self.params["xsp"] = NMLParam(
            "xsp", float, xsp, units="(mmol P) (g OM)^{-1}"
        )
        self.params["fsed_doc"] = NMLParam(
            "fsed_doc", float, fsed_doc, units="(mmol C) m^{-2} day^{-1}"
        )
        self.params["fsed_don"] = NMLParam(
            "fsed_don", float, fsed_don, units="(mmol N) m^{-2} day^{-1}"
        )
        self.params["fsed_dop"] = NMLParam(
            "fsed_dop", float, fsed_dop, units="(mmol P) m^{-2} day^{-1}"
        )
        self.params["ksed_dom"] = NMLParam(
            "ksed_dom", float, ksed_dom, units="(mmol O_{2}) m^{-3}"
        )
        self.params["theta_sed_dom"] = NMLParam(
            "theta_sed_dom", float, theta_sed_dom
        )
        self.params["fsed_doc_variable"] = NMLParam(
            "fsed_doc_variable",
            str,
            fsed_doc_variable,
            units="(mmol C) m^{-2} day^{-1}",
        )
        self.params["fsed_don_variable"] = NMLParam(
            "fsed_don_variable",
            str,
            fsed_don_variable,
            units="(mmol N) m^{-2} day^{-1}",
        )
        self.params["fsed_dop_variable"] = NMLParam(
            "fsed_dop_variable",
            str,
            fsed_dop_variable,
            units="(mmol P) m^{-2} day^{-1}",
        )
        self.params["diag_level"] = NMLParam("diag_level", int, diag_level)

    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class PhytoplanktonBlock(NMLBlock):
    block_name = "aed_phytoplankton"

    def __init__(
        self,
        num_phytos: Union[int, None] = None,
        the_phytos: Union[List[int], None] = None,
        settling: Union[List[int], None] = None,
        p_excretion_target_variable: Union[str, None] = None,
        n_excretion_target_variable: Union[str, None] = None,
        c_excretion_target_variable: Union[str, None] = None,
        si_excretion_target_variable: Union[str, None] = None,
        p_mortality_target_variable: Union[str, None] = None,
        n_mortality_target_variable: Union[str, None] = None,
        c_mortality_target_variable: Union[str, None] = None,
        si_mortality_target_variable: Union[str, None] = None,
        p1_uptake_target_variable: Union[str, None] = None,
        n1_uptake_target_variable: Union[str, None] = None,
        n2_uptake_target_variable: Union[str, None] = None,
        si_uptake_target_variable: Union[str, None] = None,
        do_uptake_target_variable: Union[str, None] = None,
        c_uptake_target_variable: Union[str, None] = None,
        dbase: Union[str, None] = None,
        min_rho: Union[float, None] = None,
        max_rho: Union[float, None] = None,
        diag_level: Union[int, None] = None,
    ):
        super().__init__()
        self.params["num_phytos"] = NMLParam("num_phytos", int, num_phytos)
        self.params["the_phytos"] = NMLParam(
            "the_phytos", int, the_phytos, is_list=True
        )
        self.params["settling"] = NMLParam(
            "settling", int, settling, is_list=True
        )
        self.params["p_excretion_target_variable"] = NMLParam(
            "p_excretion_target_variable", str, p_excretion_target_variable
        )
        self.params["n_excretion_target_variable"] = NMLParam(
            "n_excretion_target_variable", str, n_excretion_target_variable
        )
        self.params["c_excretion_target_variable"] = NMLParam(
            "c_excretion_target_variable", str, c_excretion_target_variable
        )
        self.params["si_excretion_target_variable"] = NMLParam(
            "si_excretion_target_variable", str, si_excretion_target_variable
        )
        self.params["p_mortality_target_variable"] = NMLParam(
            "p_mortality_target_variable", str, p_mortality_target_variable
        )
        self.params["n_mortality_target_variable"] = NMLParam(
            "n_mortality_target_variable", str, n_mortality_target_variable
        )
        self.params["c_mortality_target_variable"] = NMLParam(
            "c_mortality_target_variable", str, c_mortality_target_variable
        )
        self.params["si_mortality_target_variable"] = NMLParam(
            "si_mortality_target_variable", str, si_mortality_target_variable
        )
        self.params["p1_uptake_target_variable"] = NMLParam(
            "p1_uptake_target_variable", str, p1_uptake_target_variable
        )
        self.params["n1_uptake_target_variable"] = NMLParam(
            "n1_uptake_target_variable", str, n1_uptake_target_variable
        )
        self.params["n2_uptake_target_variable"] = NMLParam(
            "n2_uptake_target_variable", str, n2_uptake_target_variable
        )
        self.params["si_uptake_target_variable"] = NMLParam(
            "si_uptake_target_variable", str, si_uptake_target_variable
        )
        self.params["do_uptake_target_variable"] = NMLParam(
            "do_uptake_target_variable", str, do_uptake_target_variable
        )
        self.params["c_uptake_target_variable"] = NMLParam(
            "c_uptake_target_variable", str, c_uptake_target_variable
        )
        self.params["dbase"] = NMLParam(
            "dbase", str, dbase
        )
        self.params["min_rho"] = NMLParam(
            "min_rho", float, min_rho
        )
        self.params["max_rho"] = NMLParam(
            "max_rho", float, max_rho
        )
        self.params["diag_level"] = NMLParam(
            "diag_level", int, diag_level
        )
    
    def validate(self):
        self.params.validate()
        self.val_list_len_params("num_phytos", "the_phytos")
        self.val_list_len_params("num_phytos", "settling")


@BLOCK_REGISTER.register()
class ZooplanktonBlock(NMLBlock):
    block_name = "aed_zooplankton"

    def __init__(
        self,
        num_zoops: Union[int, None] = None,
        the_zoops: Union[List[int], None] = None,
        dn_target_variable: Union[str, None] = None,
        pn_target_variable: Union[str, None] = None,
        dp_target_variable: Union[str, None] = None,
        pp_target_variable: Union[str, None] = None,
        dc_target_variable: Union[str, None] = None,
        pc_target_variable: Union[str, None] = None,
        dbase: Union[str, None] = None,
        simzoopfeedback: Union[bool, None] = None,
    ):
        super().__init__()
        self.params["num_zoops"] = NMLParam("num_zoops", int, num_zoops)
        self.params["the_zoops"] = NMLParam(
            "the_zoops", int, the_zoops, is_list=True
        )
        self.params["dn_target_variable"] = NMLParam(
            "dn_target_variable", str, dn_target_variable
        )
        self.params["pn_target_variable"] = NMLParam(
            "pn_target_variable", str, pn_target_variable
        )
        self.params["dp_target_variable"] = NMLParam(
            "dp_target_variable", str, dp_target_variable
        )
        self.params["pp_target_variable"] = NMLParam(
            "pp_target_variable", str, pp_target_variable
        )
        self.params["dc_target_variable"] = NMLParam(
            "dc_target_variable", str, dc_target_variable
        )
        self.params["pc_target_variable"] = NMLParam(
            "pc_target_variable", str, pc_target_variable
        )
        self.params["dbase"] = NMLParam(
            "dbase", str, dbase
        )
        self.params["simzoopfeedback"] = NMLParam(
            "simzoopfeedback", bool, simzoopfeedback
        )
    
    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class MacrophyteBlock(NMLBlock):
    block_name = "aed_macrophyte"

    def __init__(
        self,
        num_mphy: Union[int, None] = None,
        the_mphy: Union[List[int], None] = None,
        n_zones: Union[int, None] = None,
        active_zones: Union[List[int], None] = None,
        simstaticbiomass: Union[bool, None] = None,
        simmacfeedback: Union[bool, None] = None,
        dbase: Union[str, None] = None,
    ):
        super().__init__()
        self.params["num_mphy"] = NMLParam("num_mphy", int, num_mphy)
        self.params["the_mphy"] = NMLParam(
            "the_mphy", int, the_mphy, is_list=True
        )
        self.params["n_zones"] = NMLParam("n_zones", int, n_zones)
        self.params["active_zones"] = NMLParam(
            "active_zones", int, active_zones, is_list=True
        )
        self.params["simstaticbiomass"] = NMLParam(
            "simstaticbiomass", bool, simstaticbiomass
        )
        self.params["simmacfeedback"] = NMLParam(
            "simmacfeedback", bool, simmacfeedback
        )
        self.params["dbase"] = NMLParam("dbase", str, dbase)

    def validate(self):
        self.params.validate()
        self.val_list_len_params("num_mphy", "the_mphy")
        self.val_list_len_params("n_zones", "active_zones")


class AEDNML(NML):
    nml_name = "aed"

    def __init__(
        self,
        aed_models: Union[ModelsBlock, None] = None,
        aed_sedflux: Union[SedFluxBlock, None] = None,
        aed_sed_const2d: Union[SedConst2DBlock, None] = None,
        aed_oxygen: Union[OxygenBlock, None] = None,
        aed_silica: Union[SilicaBlock, None] = None,
        aed_nitrogen: Union[NitrogenBlock, None] = None,
        aed_phosphorus: Union[PhosphorusBlock, None] = None,
        aed_organic_matter: Union[OrganicMatterBlock, None] = None,
        aed_phytoplankton: Union[PhytoplanktonBlock, None] = None,
        aed_zooplankton: Union[ZooplanktonBlock, None] = None,
        aed_macrophyte: Union[MacrophyteBlock, None] = None,
    ):
        super().__init__()
        self.blocks["aed_models"] = aed_models
        self.blocks["aed_sedflux"] = aed_sedflux
        self.blocks["aed_sed_const2d"] = aed_sed_const2d
        self.blocks["aed_oxygen"] = aed_oxygen
        self.blocks["aed_silica"] = aed_silica
        self.blocks["aed_nitrogen"] = aed_nitrogen
        self.blocks["aed_phosphorus"] = aed_phosphorus
        self.blocks["aed_organic_matter"] = aed_organic_matter
        self.blocks["aed_phytoplankton"] = aed_phytoplankton
        self.blocks["aed_zooplankton"] = aed_zooplankton
        self.blocks["aed_macrophyte"] = aed_macrophyte

    def validate(self):
        self.blocks.validate()
