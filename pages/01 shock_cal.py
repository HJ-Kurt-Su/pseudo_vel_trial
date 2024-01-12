import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import numpy as np
import endaq
import io




@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')


def convert_fig(fig):

    mybuff = io.StringIO()
   
    # fig_html = fig_pair.write_html(fig_file_name)
    fig.write_html(mybuff, include_plotlyjs='cdn')
    html_bytes = mybuff.getvalue().encode()

    return html_bytes

def main():

    st.title('Shock Calculate Tool')

    st.markdown("               ")
    st.markdown("               ")

    input_method = st.selectbox("Select Input Profile:", 
                             ["User CSV Input", "Ideal Wave Profile"]
                             )
    
    if input_method == "Ideal Wave Profile":

        wave_type = st.selectbox("Select Ideal Wave Type:", 
                                ["Half-Sine", "Square"]
                                )
        
        wave_para = st.radio(
            "**Select Input Parameter:**",
            ["Duration & G", "DeltaV & G"],
            # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
            )
        
        if wave_para == "Duration & G":
            # g_lv = st.number_input("Please Input G Level (Unit: G)", min_value=0.1, value=30.0)
            duration = st.number_input("Please Input Duration (Unit: ms)", min_value=0.1, value=5.0)
            duration = duration/1000
        
        if wave_para == "DeltaV & G":
            del_v = st.number_input("Please Input Delta V (Unit: in/s)", min_value=0.1, value=30.0)
        
        g_lv = st.number_input("Please Input G Level (Unit: G)", min_value=0.1, value=30.0)
        # duration = st.number_input("Please Input Duration (Unit: ms)", min_value=0.1, value=5.0)
        del_t = st.number_input("Please Input Delta T (Unit: ms)", min_value=0.01, value=0.2)
        del_t = del_t/1000

        df_id_wv = pd.DataFrame()

        if wave_type == "Half-Sine":
            if wave_para == "DeltaV & G":
                # g_lv = (2 * np.pi * freq * del_v * 0.0254) / (9.81 * 2)  
                duration = (del_v * 0.0254 * 2 * np.pi) / (2 * 2 * g_lv *9.81)
                duration
                
            freq = 1/(2 * duration)
            time_series = np.arange(0, 6000*duration, del_t)
            df_id_wv["Time"] = time_series
            df_id_wv["G"] = g_lv*np.sin(2 * np.pi * freq * df_id_wv["Time"])
            # df_id_wv
            df_id_wv.loc[df_id_wv["Time"] > duration, "G"] = 0

        if wave_type == "Square":
            if wave_para == "DeltaV & G":
                # del_v = g_lv * 9.81 * duration  
                duration = (del_v * 0.0254) / (g_lv * 9.81)
                # g_lv   
            span = 2
            time_series = np.arange(0, 1.5*duration, del_t)
            df_id_wv["Time"] = time_series
            df_id_wv["G"] = g_lv
            df_id_wv.loc[df_id_wv["Time"] > duration+2*span*del_t, "G"] = 0
            df_id_wv.loc[df_id_wv["Time"] < span*del_t, "G"] = 0
            df_id_wv.loc[df_id_wv["Time"] > duration+span*del_t, "G"] = 0


    uploaded_csv = st.sidebar.file_uploader('#### 選擇您要上傳的 CSV 檔', type="csv")
    
    if uploaded_csv is not None:
        df_accel = pd.read_csv(uploaded_csv, encoding="utf-8")
        st.header('您所上傳的 csv 檔內容：')

    else:
        if input_method == "Ideal Wave Profile":
            st.header('Ideal Wave')
            df_accel = df_id_wv.copy()
        else:
            st.header('未上傳檔案，以下為 Demo：')
            uploaded_csv = "motorcycle-crash.csv"
            df_accel = pd.read_csv(uploaded_csv, encoding="utf-8")

    df_accel = df_accel.set_index(df_accel.columns[0])


    filter_raw = st.checkbox("Filter Raw Data")
    if filter_raw == True:
        filter_type = st.selectbox("Select Filter Type:", 
                             ["Low Pass", "Band Pass", "High Pass"]
                             )
        
        if filter_type == "Low Pass":
            cut_off = st.number_input('Cut-off Frequency (Hz)', min_value=1, value=100, step=1)
            df_accel = endaq.calc.filters.butterworth(df_accel, low_cutoff=None, high_cutoff=cut_off)

        elif filter_type == "High Pass":
            cut_off = st.number_input('Cut-off Frequency (Hz)', min_value=1, value=10, step=1)
            df_accel = endaq.calc.filters.butterworth(df_accel, low_cutoff=cut_off, high_cutoff=None)
        
        else:
            low_cut_off = st.number_input('Low Cut-off Frequency (Hz)', min_value=1, value=10, step=1)
            cut_off = st.number_input('High Cut-off Frequency (Hz)', min_value=low_cut_off, value=500, step=1)
            df_accel = endaq.calc.filters.butterworth(df_accel, low_cutoff=low_cut_off, high_cutoff=cut_off)

            
    df_accel
    # aa = df_accel.describe()
    # aa
    if input_method == "Ideal Wave Profile":

        id_wv_fil = convert_df(df_id_wv)
        id_wv_name = [wave_type, str(round(g_lv)), "G", str(round(duration*1000)), "ms", "_ideal_wv.csv"]
        fil_file_name_csv = "-".join(id_wv_name)
        # fil_file_name_csv = wave_type + g_lv + del_v + duration + "_ideal_wv.csv"

        st.download_button(label='Download wave result as CSV',  
                            data=id_wv_fil, 
                            file_name=fil_file_name_csv,
                            mime='text/csv'
                            )


    date = str(dt.datetime.now()).split(" ")[0]

    
    # df_accel

    chl_list = df_accel.columns
    default_chl = chl_list[0]
    sel_chl = st.multiselect(
        "**Choose channel for figure:**", 
        chl_list, default=default_chl
    )

    df_accel_chl = df_accel[sel_chl]

    g_unit = st.radio(
        "**What's acceleration unit:**",
        ["G", "m/s^2", "inch/s^2"],
        # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
        )
    
    # if g_unit == "G":
    #     pv_unit = ""
    
    damping = st.number_input('**Damping Ratio:**', min_value=0.01, value=0.05, step=0.01)


    cal_srs = st.checkbox("Calculate SRS", value=True)
    cal_pvss = st.checkbox("Calculate Pseduo Velocity")
    cal_psd = st.checkbox("Calculate PSD")


    color_sequence = ["#65BFA1", "#A4D6C1", "#D5EBE1", "#EBF5EC", "#00A0DF", "#81CDE4", "#BFD9E2"]
    color_sequence = px.colors.qualitative.Pastel
    template = "simple_white"


    st.markdown("     ")
    st.subheader("Raw Figure")
    fig_raw = px.line(df_accel, x=df_accel.index, y=sel_chl,
                      color_discrete_sequence=color_sequence, template=template, 
                # log_x=True, log_y=True,
                labels={
                    "value": g_unit
                },
                # range_x=[1, 1000], range_y=[1, 1000]
                )
# fig_srs.update_yaxes(title_font_family="Arial")

    st.plotly_chart(fig_raw, use_container_width=True)

    if filter_raw == True:
        filter_fil = convert_df(df_accel)
        filter_file_name_csv = filter_type + "_" + str(cut_off) + " Hz_filter.csv"

        st.download_button(label='Download filter result as CSV',  
                            data=filter_fil, 
                            file_name=filter_file_name_csv,
                            mime='text/csv'
                            )

    st.markdown("--------------------")

    if cal_srs == True:
        st.subheader("SRS")

        f_step = st.slider('Frequency Step', 5, 200, value=50, step=5)
        f_min = st.number_input('Min. Frequency (Hz)', min_value=5, value=10, step=1)
        f_max = st.number_input('Max. Frequency (Hz)', min_value=f_min, value=10000, step=100)
        


        df_accel_srs = endaq.calc.shock.shock_spectrum(df_accel_chl, freqs=range(f_min,f_max, f_step), damp=damping, mode="srs")

        
        df_accel_srs = df_accel_srs.reset_index()
        # df_accel_psd = df_accel_psd.reset_index()
        # df_accel_vc = df_accel_vc.reset_index()

        
        df_accel_srs
        # df_accel_psd
        # df_accel_vc



        fig_srs = px.line(df_accel_srs, x='frequency (Hz)', y=sel_chl,
                          color_discrete_sequence=color_sequence, template=template, 
                        log_x=True, log_y=True,
                        labels={
                            "value": g_unit
                        },
                        # range_x=[1, 1000], range_y=[1, 1000]
                        )
        # fig_srs.update_yaxes(title_font_family="Arial")
        
        st.plotly_chart(fig_srs, use_container_width=True)

        srs_fil = convert_df(df_accel_srs)
        fil_file_name_csv = date + "_srs.csv"

        st.download_button(label='Download pvss result as CSV',  
                            data=srs_fil, 
                            file_name=fil_file_name_csv,
                            mime='text/csv'
                            )


        fig_srs_name = date + "_srs.html"
        # fig_html = fig_pair.write_html(fig_file_name)
        srs_html = convert_fig(fig_srs)

        st.download_button(label="Download SRS figure",
                            data=srs_html,
                            file_name=fig_srs_name,
                            mime='text/html'
                            )
        

    # df_accel_psd = endaq.calc.psd.welch(df_accel, bin_width=1/11)
    # df_accel_vc = endaq.calc.psd.vc_curves(df_accel_psd, fstart=1, octave_bins=3)


    st.markdown("--------------------")

    if cal_pvss == True:
        st.subheader("Pseudo Velocity")
        pv_unit = st.radio(
        "## **Select pseudo velocity unit:**",
        ["m/s", "inch/s"],
        # captions = ["Laugh out loud.", "Get the popcorn.", "Never stop learning."]
        )

        

        if g_unit == "G" and pv_unit == "m/s":
            # st.markdown("try this!!!")
            df_accel_chl_pv = df_accel_chl*9.81
            # df_accel_chl
            
        elif g_unit == "G" and pv_unit == "inch/s":
            df_accel_chl_pv = df_accel_chl*9.81*39.37

        elif g_unit == "inch/s^2" and pv_unit == "m/s":
            df_accel_chl_pv = df_accel_chl*0.0254

        elif g_unit == "m/s^2" and pv_unit == "inch/s":
            df_accel_chl_pv = df_accel_chl*39.37
        else:
            df_accel_chl_pv = df_accel_chl


        
        # df_accel_pvss = endaq.calc.shock.shock_spectrum(df_accel_chl, freqs=2 ** np.arange(-10, 13, 0.25), damp=0.05, mode="pvss")
        df_accel_pvss = endaq.calc.shock.shock_spectrum(df_accel_chl_pv, damp=damping, mode="pvss")


        df_accel_pvss = df_accel_pvss.reset_index()
        df_accel_pvss
        # df_accel_pvss.columns[:-1]

        fig_pvss = px.line(df_accel_pvss, x='frequency (Hz)', y=sel_chl,
                           color_discrete_sequence=color_sequence, template=template, 
                        log_x=True, log_y=True,
                        # range_x=[1, 1000], range_y=[1, 1000]
                        labels={
                            "value": pv_unit
                        },
                        )
        
        st.plotly_chart(fig_pvss, use_container_width=True)

        pvss_fil = convert_df(df_accel_pvss)
        fil_file_name_csv = date + "_pvss.csv"

        st.download_button(label='Download pvss result as CSV',  
                            data=pvss_fil, 
                            file_name=fil_file_name_csv,
                            mime='text/csv',
                            key="pvss_csv")
        
        fig_pvss_name = date + "_pvss.html"
        # fig_html = fig_pair.write_html(fig_file_name)
        pvss_html = convert_fig(fig_pvss)

        st.download_button(label="Download PVSS figure",
                            data=pvss_html,
                            file_name=fig_pvss_name,
                            mime='text/html',
                            key="pvss_fig"
                            )
    
    
    
    if cal_psd == True:

        st.markdown("---")
        st.markdown("## Under Construnction")
        st.subheader("PSD")
        # df_accel_psd = endaq.calc.psd.to_octave(df_accel_chl, fstart=10)
        df_accel_psd = endaq.calc.psd.welch(df_accel_chl, bin_width=1, scaling="parseval")


        df_accel_psd = df_accel_psd.reset_index()
        df_accel_psd
        # df_accel_pvss.columns[:-1]

        y_label = g_unit + "-square/Hz"

        fig_psd = px.line(df_accel_psd, x='frequency (Hz)', y=sel_chl,
                          color_discrete_sequence=color_sequence, template=template, 
                        log_x=True, log_y=True,
                        # range_x=[10, 1000], 
                        # range_y=[1, 1000]
                        labels={
                            "value": y_label
                        },
                        )
        
        st.plotly_chart(fig_psd, use_container_width=True)
        st.markdown("---")
        
        psd_fil = convert_df(df_accel_psd)
        fil_file_name_csv = date + "_psd.csv"

        st.download_button(label='Download psd result as CSV',  
                            data=psd_fil, 
                            file_name=fil_file_name_csv,
                            mime='text/csv',
                            key="psd_csv")
        
        fig_psd_name = date + "_psd.html"
        # fig_html = fig_pair.write_html(fig_file_name)
        psd_html = convert_fig(fig_psd)

        st.download_button(label="Download PSD figure",
                            data=psd_html,
                            file_name=fig_psd_name,
                            mime='text/html',
                            key="psd_fig"
                            )

        



if __name__ == '__main__':
    main()
