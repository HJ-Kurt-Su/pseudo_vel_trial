import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import numpy as np
import endaq
import datetime


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

def main():

    st.title('Shock Calculate Tool')

    st.markdown("               ")
    st.markdown("               ")

    uploaded_csv = st.sidebar.file_uploader('#### 選擇您要上傳的 CSV 檔', type="csv")
    # uploaded_xl = st.sidebar.file_uploader('#### 選擇您要上傳的 Excel 檔', type="xlsx")

    # calulate month can be UI adjust, 3 means total arrange month (real + predict)
    # cal_mon = st.number_input("How Many Month To Calculate", min_value=1, max_value=10, value=3, step=1)

    # # real predict switch can be UI adjust, 1 means only 1 real month data, rest is predict
    # real_pred_swch = st.number_input("How Many Real Month", min_value=0, max_value=4, value=1, step=1)

    # # pred_mon = st.text_input("Please Provide Predict Month: ", "Y23 Aug")
    # pred_mon = st.text_input("Please Provide Predict Month: ", "Y23 Aug")
    
    if uploaded_csv is not None:
        df_accel = pd.read_csv(uploaded_csv, encoding="utf-8")
        st.header('您所上傳的 csv 檔內容：')

    else:
        st.header('未上傳檔案，以下為 Demo：')
        uploaded_csv = "motorcycle-crash.csv"
        df_accel = pd.read_csv(uploaded_csv, encoding="utf-8")
   
    df_accel
    date = str(datetime.datetime.now()).split(" ")[0]

    df_accel = df_accel.set_index(df_accel.columns[0])
    # df_accel

    chl_list = df_accel.columns
    default_chl = chl_list[0]
    sel_chl = st.multiselect(
        "### Choose channel for figure", 
        chl_list, default=default_chl
    )

    df_accel_chl = df_accel[sel_chl]

    g_unit = st.radio(
        "What's acceleration unit:",
        ["G", "m/s^2", "inch/s^2"],
        # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
        )
    
    # if g_unit == "G":
    #     pv_unit = ""
    
    damping = st.number_input('Damping Ratio', min_value=0.01, value=0.05, step=0.01)


    cal_srs = st.checkbox("Calculate SRS", value=True)
    cal_pvss = st.checkbox("Calculate Pseduo Velocity")


    if cal_srs == True:

        f_step = st.slider('Frequency Step', 5, 200, value=50, step=5)
        f_min = st.number_input('Min. Frequency (Hz)', min_value=5, value=10, step=1)
        f_max = st.number_input('Max. Frequency (Hz)', min_value=f_min, value=10000, step=100)
        


        df_accel_srs = endaq.calc.shock.shock_spectrum(df_accel_chl, freqs=range(f_min,f_max, f_step), damp=damping, mode="srs")

        st.subheader("SRS")
        df_accel_srs = df_accel_srs.reset_index()
        # df_accel_psd = df_accel_psd.reset_index()
        # df_accel_vc = df_accel_vc.reset_index()

        
        df_accel_srs
        # df_accel_psd
        # df_accel_vc



        fig_srs = px.line(df_accel_srs, x='frequency (Hz)', y=sel_chl,
                        log_x=True, log_y=True,
                        labels={
                            "value": g_unit
                        },
                        # range_x=[1, 1000], range_y=[1, 1000]
                        )
        # fig_srs.update_yaxes(title_font_family="Arial")
        
        fig_srs

        srs_fil = convert_df(df_accel_srs)
        fil_file_name_csv = date + "_srs.csv"
        st.download_button(label='Download pvss result as CSV',  
        data=srs_fil, 
        file_name=fil_file_name_csv,
        mime='text/csv')

    # df_accel_psd = endaq.calc.psd.welch(df_accel, bin_width=1/11)
    # df_accel_vc = endaq.calc.psd.vc_curves(df_accel_psd, fstart=1, octave_bins=3)


    st.markdown("--------------------")

    if cal_pvss == True:

        pv_unit = st.radio(
        "## **Select pseudo velocity unit:**",
        ["m/s", "inch/s"],
        # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
        )

        st.subheader("Pseudo Velocity")

        if g_unit == "G" and pv_unit == "m/s":
            # st.markdown("try this!!!")
            df_accel_chl = df_accel_chl*9.81
            # df_accel_chl
            
        elif g_unit == "G" and pv_unit == "inch/s":
            df_accel_chl = df_accel_chl*9.81*39.37

        elif g_unit == "inch/s^2" and pv_unit == "m/s":
            df_accel_chl = df_accel_chl*0.0254

        elif g_unit == "m/s^2" and pv_unit == "inch/s":
            df_accel_chl = df_accel_chl*39.37


        
        # df_accel_pvss = endaq.calc.shock.shock_spectrum(df_accel_chl, freqs=2 ** np.arange(-10, 13, 0.25), damp=0.05, mode="pvss")
        df_accel_pvss = endaq.calc.shock.shock_spectrum(df_accel_chl, damp=damping, mode="pvss")


        df_accel_pvss = df_accel_pvss.reset_index()
        df_accel_pvss
        # df_accel_pvss.columns[:-1]

        fig_pvss = px.line(df_accel_pvss, x='frequency (Hz)', y=sel_chl,
                        log_x=True, log_y=True,
                        # range_x=[1, 1000], range_y=[1, 1000]
                        labels={
                            "value": pv_unit
                        },
                        )
        
        fig_pvss

        pvss_fil = convert_df(df_accel_pvss)
        fil_file_name_csv = date + "_pvss.csv"
        st.download_button(label='Download pvss result as CSV',  
        data=pvss_fil, 
        file_name=fil_file_name_csv,
        mime='text/csv')

        




if __name__ == '__main__':
    main()
