from typing import Union, List
from glmpy.nml.nml import BLOCK_REGISTER, NMLParam, NMLBlock, NML


@BLOCK_REGISTER.register()
class PhytoDataBlock(NMLBlock):
    block_name = "phyto_data"
    file_name = "aed_phyto_pars"
    param_prefix = "pd%"

    def __init__(
        self,
        p_name: Union[List[str], None] = None,       
        p_initial: Union[List[float], None] = None,    
        p0: Union[List[float], None] = None,           
        xcc: Union[List[float], None] = None,          
        r_growth: Union[List[float], None] = None,     
        ft_method: Union[List[int], None] = None,    
        theta_growth: Union[List[float], None] = None, 
        t_std: Union[List[float], None] = None,        
        t_opt: Union[List[float], None] = None,        
        t_max: Union[List[float], None] = None,        
        lightmodel: Union[List[int], None] = None,   
        i_k: Union[List[float], None] = None,          
        i_s: Union[List[float], None] = None,          
        kephy: Union[List[float], None] = None,        
        f_pr: Union[List[float], None] = None,         
        r_resp: Union[List[float], None] = None,       
        theta_resp: Union[List[float], None] = None,   
        k_fres: Union[List[float], None] = None,       
        k_fdom: Union[List[float], None] = None,       
        saltol: Union[List[int], None] = None,       
        s_bep: Union[List[float], None] = None,        
        s_maxsp: Union[List[float], None] = None,      
        s_opt: Union[List[float], None] = None,        
        simdinuptake: Union[List[int], None] = None, 
        simdonuptake: Union[List[int], None] = None, 
        simnfixation: Union[List[int], None] = None, 
        simindynamics: Union[List[int], None] = None,
        n_o: Union[List[float], None] = None,          
        k_n: Union[List[float], None] = None,          
        x_ncon: Union[List[float], None] = None,       
        x_nmin: Union[List[float], None] = None,       
        x_nmax: Union[List[float], None] = None,       
        r_nuptake: Union[List[float], None] = None,    
        k_nfix: Union[List[float], None] = None,       
        r_nfix: Union[List[float], None] = None,       
        simdipuptake: Union[List[int], None] = None, 
        simipdynamics: Union[List[int], None] = None,
        p_0: Union[List[float], None] = None,          
        k_p: Union[List[float], None] = None,          
        x_pcon: Union[List[float], None] = None,       
        x_pmin: Union[List[float], None] = None,       
        x_pmax: Union[List[float], None] = None,       
        r_puptake: Union[List[float], None] = None,    
        simsiuptake: Union[List[int], None] = None,  
        si_0: Union[List[float], None] = None,         
        k_si: Union[List[float], None] = None,         
        x_sicon: Union[List[float], None] = None,      
        w_p: Union[List[float], None] = None,          
        c1: Union[List[float], None] = None,           
        c3: Union[List[float], None] = None,           
        f1: Union[List[float], None] = None,           
        f2: Union[List[float], None] = None,           
        d_phy: Union[List[float], None] = None,        
    ):
        super().__init__()
        self.params["p_name"] = NMLParam("p_name", str, p_name, is_list=True)
        self.params["p_initial"] = NMLParam("p_initial", float, p_initial, is_list=True)
        self.params["p0"] = NMLParam("p0", float, p0, is_list=True)
        self.params["xcc"] = NMLParam("xcc", float, xcc, is_list=True)
        self.params["r_growth"] = NMLParam("r_growth", float, r_growth, is_list=True)
        self.params["ft_method"] = NMLParam("ft_method", int, ft_method, is_list=True)
        self.params["theta_growth"] = NMLParam("theta_growth", float, theta_growth, is_list=True)
        self.params["t_std"] = NMLParam("t_std", float, t_std, is_list=True)
        self.params["t_opt"] = NMLParam("t_opt", float, t_opt, is_list=True)
        self.params["t_max"] = NMLParam("t_max", float, t_max, is_list=True)
        self.params["lightmodel"] = NMLParam("lightmodel", int, lightmodel, is_list=True)
        self.params["i_k"] = NMLParam("i_k", float, i_k, is_list=True)
        self.params["i_s"] = NMLParam("i_s", float, i_s, is_list=True)
        self.params["kephy"] = NMLParam("kephy", float, kephy, is_list=True)
        self.params["f_pr"] = NMLParam("f_pr", float, f_pr, is_list=True)
        self.params["r_resp"] = NMLParam("r_resp", float, r_resp, is_list=True)
        self.params["theta_resp"] = NMLParam("theta_resp", float, theta_resp, is_list=True)
        self.params["k_fres"] = NMLParam("k_fres", float, k_fres, is_list=True)
        self.params["k_fdom"] = NMLParam("k_fdom", float, k_fdom, is_list=True)
        self.params["saltol"] = NMLParam("saltol", int, saltol, is_list=True)
        self.params["s_bep"] = NMLParam("s_bep", float, s_bep, is_list=True)
        self.params["s_maxsp"] = NMLParam("s_maxsp", float, s_maxsp, is_list=True)
        self.params["s_opt"] = NMLParam("s_opt", float, s_opt, is_list=True)
        self.params["simdinuptake"] = NMLParam("simdinuptake", int, simdinuptake, is_list=True)
        self.params["simdonuptake"] = NMLParam("simdonuptake", int, simdonuptake, is_list=True)
        self.params["simnfixation"] = NMLParam("simnfixation", int, simnfixation, is_list=True)
        self.params["simindynamics"] = NMLParam("simindynamics", int, simindynamics, is_list=True)
        self.params["n_o"] = NMLParam("n_o", float, n_o, is_list=True)
        self.params["k_n"] = NMLParam("k_n", float, k_n, is_list=True)
        self.params["x_ncon"] = NMLParam("x_ncon", float, x_ncon, is_list=True)
        self.params["x_nmin"] = NMLParam("x_nmin", float, x_nmin, is_list=True)
        self.params["x_nmax"] = NMLParam("x_nmax", float, x_nmax, is_list=True)
        self.params["r_nuptake"] = NMLParam("r_nuptake", float, r_nuptake, is_list=True)
        self.params["k_nfix"] = NMLParam("k_nfix", float, k_nfix, is_list=True)
        self.params["r_nfix"] = NMLParam("r_nfix", float, r_nfix, is_list=True)
        self.params["simdipuptake"] = NMLParam("simdipuptake", int, simdipuptake, is_list=True)
        self.params["simipdynamics"] = NMLParam("simipdynamics", int, simipdynamics, is_list=True)
        self.params["p_0"] = NMLParam("p_0", float, p_0, is_list=True)
        self.params["k_p"] = NMLParam("k_p", float, k_p, is_list=True)
        self.params["x_pcon"] = NMLParam("x_pcon", float, x_pcon, is_list=True)
        self.params["x_pmin"] = NMLParam("x_pmin", float, x_pmin, is_list=True)
        self.params["x_pmax"] = NMLParam("x_pmax", float, x_pmax, is_list=True)
        self.params["r_puptake"] = NMLParam("r_puptake", float, r_puptake, is_list=True)
        self.params["simsiuptake"] = NMLParam("simsiuptake", int, simsiuptake, is_list=True)
        self.params["si_0"] = NMLParam("si_0", float, si_0, is_list=True)
        self.params["k_si"] = NMLParam("k_si", float, k_si, is_list=True)
        self.params["x_sicon"] = NMLParam("x_sicon", float, x_sicon, is_list=True)
        self.params["w_p"] = NMLParam("w_p", float, w_p, is_list=True)
        self.params["c1"] = NMLParam("c1", float, c1, is_list=True)
        self.params["c3"] = NMLParam("c3", float, c3, is_list=True)
        self.params["f1"] = NMLParam("f1", float, f1, is_list=True)
        self.params["f2"] = NMLParam("f2", float, f2, is_list=True)
        self.params["d_phy"] = NMLParam("d_phy", float, d_phy, is_list=True)
    
    def validate(self):
        self.params.validate()


@BLOCK_REGISTER.register()
class ZoopParamsBlock(NMLBlock):
    block_name = "zoop_params"
    file_name = "aed_zoop_pars"
    param_prefix = "zoop_param%"

