import math, pvlib
import numpy as np
import pandas as pd
from scipy.special import lambertw
from scipy.optimize import root_scalar, fsolve

#import math, pvlib, warnings

def changeUnitsK(K, Base):
    return (Base*K)/100

def Eq_Toper(TONC, G, Tamb):
    Toper = Tamb + ((TONC - 20)/800)*G
    return Toper

def Eq_Vt(K, Toper, q):
    return (K*Toper)/q

def Eq_13(k, Tstc, data_pv, Vt, Iph):
    num = data_pv['Beta']-(data_pv['Voc']/Tstc)
    den = data_pv['Ns']*Vt*((data_pv['Alfa']/Iph)-(3/Tstc)-(data_pv['Egap']/(k*(Tstc**2))))
    n = num/den

    return n

def Eq_14(data_pv, nNsVt, Iph):
    return Iph*math.exp((-1*data_pv['Voc'])/(nNsVt))

def Eq_15(data_pv, T, Vt, Isat):
    return Isat/((T**3)*np.exp((-1*data_pv['Egap'])/Vt))

def Eq_28(data_pv, Vt, n, Iph, Isat):
    num = data_pv['Vmpp']*(2*data_pv['Impp']-Iph)*math.exp(data_pv['Vmpp']*(data_pv['Vmpp']-2*data_pv['Ns']*n*Vt))/(data_pv['Ns']*(n**2)*(Vt**2))
    den = data_pv['Ns']*n*Isat*Vt
    
    t1 = np.real(lambertw(num/den))
    t2 = 2*(data_pv['Vmpp']/(data_pv['Ns']*n*Vt))
    t3 = (data_pv['Vmpp']**2)/(data_pv['Ns']*(n**2)*(Vt**2))

    x = t1 + t2 - t3

    return x*math.exp(x)

def Eq_26(data_pv, nNsVt, Iph, Isat):
    def fx(x):
        return data_pv['Vmpp']*(2*data_pv['Impp']-Iph)+Isat*np.exp(x)*(-1*nNsVt*x+data_pv['Vmpp']*(2-(data_pv['Vmpp']/(nNsVt))))

    sol = root_scalar(fx, x0=-1, method='bisect', bracket=[-50, 50])
    x = sol.root

    return x

def Eq_17(data_pv, nNsVt, x):
    return ((x*nNsVt)-data_pv['Vmpp'])/data_pv['Impp']

def Eq_19(data_pv, nNsVt, Iph, Isat, x):
    num = x*nNsVt
    den = Iph - data_pv['Impp'] - Isat*(math.exp(x)-1)
    Rp = num/den

    return Rp

def Iph_oper(data_pv, param_pv, Geff, Toper):
    Tstc, Gref = 299.15, 1000
    return (Geff/Gref)*(param_pv['Iph'] + data_pv['Alfa']*(Toper-Tstc))

def Isat_oper(data_pv, param_pv, Vt, Toper): 
    return param_pv['Cstc']*(Toper**3)*np.exp(-1*data_pv['Egap']/Vt)

def parameters_values(data_pv):

    # Constantes:
    k = 1.3806503e-23
    q = 1.60217646e-19
    Tstc = 299.15
    
    # Vt: Voltaje térmico (V)
    Vt = Eq_Vt(k, Tstc, q)

    # Iph: Corriente fotoinducida (A)
    Iph = data_pv['Isc']

    # n: Factor de idealidad del diodo
    n = Eq_13(k, Tstc, data_pv, Vt, Iph)

    # nNsVt
    nNsVt = n*data_pv['Ns']*Vt

    # Isat: Corriente de saturación del diodo (A)
    Isat = Eq_14(data_pv, nNsVt, Iph)
    Cstc = Eq_15(data_pv, Tstc, Vt, Isat)

    # Ecuación 26 
    x = Eq_26(data_pv, nNsVt, Iph, Isat)

    # Rs: Resistencia serie (Ohm)
    Rs = Eq_17(data_pv, nNsVt, x)

    # Rp: Resistencia en paralelo (Ohm)
    Rp = Eq_19(data_pv, nNsVt, Iph, Isat, x)

    param_pv = {
        'Iph': Iph,
        'n': n,
        'nNsVt': nNsVt,
        'Isat': Isat,
        'Cstc': Cstc,
        'Rs': Rs,
        'Rp': Rp,
        'Egap': data_pv['Egap']
        }

    return param_pv

def get_STD_params(Voc, Isc, Vmpp, Impp, Alfa, Beta, Delta, NOCT, Ns, cell_type, dict_value_Egap):

    data_pv = {'Voc': Voc,
               'Isc': Isc,
               'Vmpp': Vmpp,
               'Impp': Impp,
               'Alfa': changeUnitsK(Alfa, Base=Isc),
               'Beta': changeUnitsK(Beta, Base=Voc),
               'Delta': Delta,
               'TONC': NOCT,
               'Ns': Ns,
               'Egap': 1.6022E-19*dict_value_Egap[cell_type]['EgRef']
               }
    
    param_pv = parameters_values(data_pv)

    SDE_params = {'photocurrent': param_pv['Iph'],
                  'saturation_current': param_pv['Isat'],
                  'resistance_series': param_pv['Rs'],
                  'resistance_shunt': param_pv['Rp'],
                  'nNsVth': param_pv['nNsVt']
                  }

    return data_pv, param_pv, SDE_params

def get_values_curve_I_V(SDE_params):
    curve_info = pvlib.pvsystem.singlediode(method='lambertw', **SDE_params)
    v = np.linspace(0., curve_info['v_oc'], 100)
    i = pvlib.pvsystem.i_from_v(voltage=v, method='lambertw', **SDE_params)
    p = v*i

    return v, i, p

def get_values_curve_I_V_version2(SDE_params):
    curve_info = pvlib.pvsystem.singlediode(method='lambertw', **SDE_params)
    v = pd.DataFrame(np.linspace(0., curve_info['v_oc'], 100))
    i = pd.DataFrame(pvlib.pvsystem.i_from_v(voltage=v, method='lambertw', **SDE_params))
    p = v*i

    return curve_info, v, i, p

def get_fit_cec_sam(cell_type, Vmpp, Impp, Voc, Isc, Alfa, Beta, Delta, Ns):

    parameters = {
        'celltype': cell_type,
        'v_mp': Vmpp,
        'i_mp': Impp,
        'v_oc': Voc,
        'i_sc': Isc,
        'alpha_sc': changeUnitsK(Alfa, Base=Isc),
        'beta_voc': changeUnitsK(Beta, Base=Voc),
        'gamma_pmp': Delta,
        'cells_in_series': Ns,
        'temp_ref': 25
    }

    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = pvlib.ivtools.sdm.fit_cec_sam(**parameters)

    return I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust

def get_calcparams_desoto(Geff, Tcell, Alfa, SDE_params, cell_type, dict_value_Egap, array_serie, array_parallel):

    cases = [(1000, 25), (Geff, Tcell)]
    conditions = pd.DataFrame(cases, columns=['Geff', 'Tcell'])

    parameters = {
        'effective_irradiance': conditions['Geff'],
        'temp_cell': conditions['Tcell'],
        'alpha_sc': changeUnitsK(Alfa, Base=SDE_params['photocurrent']),
        'a_ref': SDE_params['nNsVth'],
        'I_L_ref': SDE_params['photocurrent'],
        'I_o_ref': SDE_params['saturation_current'],
        'R_sh_ref': SDE_params['resistance_shunt'],
        'R_s': SDE_params['resistance_series'],
        'EgRef': dict_value_Egap[cell_type]['EgRef'],
        'dEgdT': -0.0002677,
        'irrad_ref': 1000,
        'temp_ref': 25
    }

    photocurrent, saturation_current, resistance_series, resistance_shunt, nNsVth = pvlib.pvsystem.calcparams_desoto(**parameters)

    SDE_params = {
        'photocurrent': photocurrent*array_parallel,
        'saturation_current': saturation_current*array_parallel,
        'resistance_series': resistance_series*(array_serie/array_parallel),
        'resistance_shunt': resistance_shunt*(array_serie/array_parallel),
        'nNsVth': nNsVth*array_serie
    }

    return conditions, SDE_params

def get_list_tabs_graph(data_columns: list, options_columns_name: list, list_options_columns_label):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(data_columns),1):
        if data_columns[i] in options_columns_name:
            list_tabs_graph_name.append(data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[options_columns_name.index(data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label