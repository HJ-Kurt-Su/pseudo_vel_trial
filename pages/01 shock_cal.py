import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import numpy as np
import endaq


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

    df_accel = df_accel.set_index("Time")
    df_accel

    # df_accel_pvss = endaq.calc.shock.shock_spectrum(df_accel, freqs=2 ** np.arange(-10, 13, 0.25), damp=0.05, mode="pvss")
    # df_accel_srs = endaq.calc.shock.shock_spectrum(df_accel, freqs=[1, 5, 10, 50, 100, 500, 1000, 5000, 10000], damp=0.05, mode="srs")

    df_accel_psd = endaq.calc.psd.welch(df_accel, bin_width=1/11)
    df_accel_vc = endaq.calc.psd.vc_curves(df_accel_psd, fstart=1, octave_bins=3)

    # df_accel_pvss = df_accel_pvss.reset_index()
    # df_accel_srs = df_accel_srs.reset_index()
    df_accel_psd = df_accel_psd.reset_index()
    df_accel_vc = df_accel_vc.reset_index()

    # df_accel_pvss
    # df_accel_srs
    df_accel_psd
    df_accel_vc

    # fig_pvss = px.line(df_accel_pvss, x='frequency (Hz)', y='Acc',
    #                    log_x=True, log_y=True,
    #                    range_x=[1, 1000], range_y=[1, 1000]
    #                    )
    # fig_pvss


if __name__ == '__main__':
    main()
