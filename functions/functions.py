from scipy.special import lambertw
from scipy.optimize import root_scalar, fsolve
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
import datetime as dt
import pandas as pd
import numpy as np
import math, pvlib, warnings

import streamlit as st

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('chained_assignment',None)

def cal_rows(date_ini, date_end, steps):
    date_delta = date_end - date_ini
    cal_rows = int((date_delta.days * 1440)/steps)

    return cal_rows

def name_file(name):
    now = dt.datetime.now()
    cadena = "[{0}-{1}-{2}-{3}-{4}]".format(now.day,
                                            now.month,
                                            now.year,
                                            now.hour,
                                            now.minute)
    
    return f"{cadena} {name}"

def get_dataframe_components(content, index_col, header, sheet_name, transpose, rename_axis):
    
    df_database = pd.read_excel(content, index_col=index_col, header=header,
                                sheet_name=sheet_name)
    
    if transpose:
        df_database = df_database.transpose()
        df_database.columns = df_database.iloc[0]
        df_database = df_database[1:].reset_index(drop=True)
        df_database.reset_index(drop=True, inplace=True)
        df_database = df_database.loc[:, :].replace(np.nan, "")

    if rename_axis != None:
        df_database = df_database.rename_axis(rename_axis)

    return df_database

def get_dataframe_display(dataframe):
    list_aux = list(dataframe.columns)[1:]
    dict_dataframe_display = {}
    dict_dataframe_display["y"] = list_aux
    dict_dataframe_display["data"] = dataframe[list_aux]
    
    return dict_dataframe_display

def get_filtering_options_pv(dataframe):

    dict_data_filter_pv = {
        'min_Wp': dataframe['Pmax (Wp)'].min(),
        'max_Wp': dataframe['Pmax (Wp)'].max(),
        'min_Voc': dataframe['Voc (V)'].min(),
        'max_Voc': dataframe['Voc (V)'].max(),
        'min_Isc': dataframe['Isc (A)'].min(),
        'max_Isc': dataframe['Isc (A)'].max(),
        'list_cell_type': list(dataframe['Tecnología'].unique()),
        'list_manufacturer': list(dataframe['Fabricante'].unique())
    }

    return dict_data_filter_pv

def get_dict_change_column_name(dataframe, option):
    dict_change_column = {}

    if option == 'pv':
        dict_change_column['Manufacturer'] = 'Fabricante'
        dict_change_column['Model'] = 'Modelo'
        dict_change_column['Pnom'] = 'Pmax (Wp)'
        dict_change_column['celltype'] = 'Tecnología'
        dict_change_column['v_mp'] = 'Vmpp (V)'
        dict_change_column['i_mp'] = 'Impp (A)'
        dict_change_column['v_oc'] = 'Voc (V)'
        dict_change_column['i_sc'] = 'Isc (A)'
        dict_change_column['alpha_sc'] = 'coeficiente Isc (A/°C)'
        dict_change_column['beta_voc'] = 'coeficiente Voc (V/°C)'
        dict_change_column['gamma_pmp'] = 'coeficiente Pmax (%/°C)'
        dict_change_column['cells_in_series'] = 'Celdas en serie'
        dict_change_column['NOCT'] = 'NOCT (°C)'
        dict_change_column['Datasheets'] = 'Hoja de datos'

    return dataframe.rename(columns=dict_change_column)

def get_dataframe_option_components(option):

    if option == '🪟 Módulos fotovoltaicos':
        file_name = "components/information/photovoltaic_panels/database.xlsx"

    return

# Modelo Panel Fotovoltaico --------------------------------------------------------------------

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

# Apps Módulos fotovoltaicos:

def add_column_dates(dataframe, date_ini, rows, steps):

    list_columns = list(dataframe.columns)
    if not "dates (Y-M-D hh:mm:ss)" in list_columns:
        dates = pd.date_range(start=date_ini,
                              periods=rows,
                              freq=pd.Timedelta(minutes=steps))
        
        if dataframe.shape[0] >= dates.shape[0]:
            dataframe = dataframe.head(rows)

        if dataframe.shape[0] == dates.shape[0]:
            dataframe["dates (Y-M-D hh:mm:ss)"] = dates
            dataframe = dataframe[["dates (Y-M-D hh:mm:ss)"] + list_columns]

    return dataframe

def get_dataframe_NASA_POWER(latitude, longitude, start, end, parameters):

    dataframe = query_power(geometry = point(x=longitude, y=latitude, crs="EPSG:4326"),
                            start = start,
                            end = end,
                            to_file = False,
                            community = "re",
                            parameters = parameters,
                            temporal_api = "hourly",
                            spatial_api = "point")

    list_columns, list_columns_drop = list(dataframe.columns), ["YEAR", "MO", "DY", "HR"]

    for i in range(0,len(list_columns_drop),1):
        if list_columns_drop[i] in list_columns:
            dataframe = dataframe.drop(columns=[list_columns_drop[i]])
        
    if "ALLSKY_SFC_SW_DWN" in list_columns:
        dataframe = dataframe.rename(columns={"ALLSKY_SFC_SW_DWN": "Gin(W/m²)"})

    return dataframe

def get_list_tabs_graph(list_data_columns, list_options_columns_name, list_options_columns_label):

    list_tabs_graph_name, list_tabs_graph_label = [], []
    for i in range(0,len(list_data_columns),1):
        if list_data_columns[i] in list_options_columns_name:
            list_tabs_graph_name.append(list_data_columns[i])
            list_tabs_graph_label.append(list_options_columns_label[list_options_columns_name.index(list_data_columns[i])])

    return list_tabs_graph_name, list_tabs_graph_label

# Apps Baterías:

def get_battery_parameters(points: dict) -> dict:
    
    q1, v1 = points['P1']
    q2, v2 = points['P2']
    q3, v3 = points['P3']
    q4, v4 = points['P4']
    q5, v5 = points['P5']
    q6, v6 = points['P6_i2']
    qi1, qi2 = points['Qi']
    i1, i2 = points['i']

    alpha = np.log(qi2/qi1)/np.log(i2/i1)

    B = (-1/q2)*np.log(((v1-v3)/(v1-v2))-1)
    A = (v1-v3)/(1-np.exp(-B*q3))

    AB4 = v1 - v4 - A*(1 - np.exp(-B*q4))
    AB5 = v1 - v5 - A*(1 - np.exp(-B*q5))

    m = (1 - (AB5/AB4))/(1 - ((AB5*q4)/(AB4*q5)))*(q4/qi1)
    K = AB5*((m*(qi1/q5)) - 1)
    
    opr_R1 = v6 + K*((m*qi2)/(m*qi2-q6)) - A*np.exp(-B*q6)
    opr_R2 = v3 + K*((m*qi1)/(m*qi1-q3)) - A*np.exp(-B*q3)

    R = (1/(i1-i2))*(opr_R1 - opr_R2)

    v0 = v1 + R*i1 + K - A

    parameters = {
        'B': B,
        'A': A,
        'm': m,
        'K': K,
        'R': R,
        'V0': v0,
        'alpha': alpha,
        }
    
    return parameters

def get_battery_graph(parameters: dict, params_nominal: dict, battery_points: dict, SOC_0: int, it_0: int, time: int, current: int):

    Qnom, Vnom, Inom = params_nominal["Qnom"], params_nominal["Vnom"], params_nominal["Inom"]
    Qmax = battery_points["P5"][0]

    time_h = time/60
    time_vector = np.arange(0, time_h, time_h/100).tolist()

    SOC, it = SOC_0, it_0

    list_prueba = []

    cont = 0
    while (SOC >= 0 or it <= Qnom) and cont < len(time_vector):
        t_h = time_vector[cont]
        it = it_0 + current*t_h
        SOC = SOC_0 - it/Qnom

        st.text(f"{t_h}, {it}, {SOC}")

        cont = cont + 1

    return time_vector
