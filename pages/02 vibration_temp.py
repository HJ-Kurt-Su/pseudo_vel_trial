import math
import numpy as np
import plotly.express as px
import streamlit as st
import pandas as pd
import endaq
# from matplotlib import pyplot as plt


def ifft_df(df, sample_rate):
  """
  將 Pandas dataframe 格式的頻域訊號，轉換成 time domain。

  Args:
    df: 包含頻域訊號的 Pandas dataframe。

  Returns:
    包含 time domain 訊號的 Pandas dataframe。
  """

  # 取得頻域訊號的資料。
  f = df.index
  amp = df.amp
  phase = df.phase

  # 計算 IFFT。
  y = np.fft.ifft(2000*amp * np.exp(1j * phase))

  # 建立新的 Pandas dataframe。
  df_time = pd.DataFrame({
    "t": f * sample_rate,
    "y": y.real,
  })

  return df_time


def main():

    st.title('Vibration Calculate Tool')

    st.markdown("               ")
    st.markdown("               ")

    """
    產生白噪音時間訊號。

    Args:
    n_samples: 訊號長度。
    sample_rate: 取樣率。
    stddev: 標準差。

    Returns:
    包含白噪音時間訊號的 Pandas dataframe。
    """

    # 產生白噪音資料。
    stddev = 1
    n_samples = 4000
    sample_rate = 200

    y = np.random.normal(0, stddev, n_samples)

    # 建立新的 Pandas dataframe。
    df_wn = pd.DataFrame({
    "time": np.arange(0, n_samples / sample_rate, 1 / sample_rate),
    "amp": y,
    })

    df_wn
    aa = df_wn.describe()
    aa
    fig_wn = px.line(df_wn, x="time", y="amp",
                    # color_discrete_sequence=color_sequence, template=template, 
                # log_x=True, log_y=True,
                # range_x=[1, 1000], range_y=[1, 1000]
                labels={
                    "value": "value_d"
                },
                )

    st.plotly_chart(fig_wn, use_container_width=True)
    df_wn = df_wn.set_index(df_wn.columns[0])

    df_fft = endaq.calc.fft.fft(df_wn, output="magnitude")
    # df_fft = endaq.calc.fft.aggregate_fft(df_wn, bin_width=5)
    df_fft_al = endaq.calc.fft.fft(df_wn, output="angle")
    df_fft["phase"] = df_fft_al["amp"]
    # df_fft_al

    df_fft

    df_ifft = ifft_df(df_fft, sample_rate)
    df_ifft

    # df_fft = df_fft.reset_index()

    # fig_fft = px.line(df_fft, x='frequency (Hz)', y="amp",
    #             # color_discrete_sequence=color_sequence, template=template, 
    #         # log_x=True, log_y=True,
    #         # range_x=[1, 1000], range_y=[1, 1000]
    #         labels={
    #             "value": "mag"
    #         },
    #         )
    # st.plotly_chart(fig_fft, use_container_width=True)

    df_ifft = df_ifft.reset_index()
    aa = df_ifft.describe()
    aa

    fig_ifft = px.line(df_ifft, x='t', y="y",
                # color_discrete_sequence=color_sequence, template=template, 
            # log_x=True, log_y=True,
            # range_x=[1, 1000], range_y=[1, 1000]
            labels={
                "value": "mag"
            },
            )
    st.plotly_chart(fig_ifft, use_container_width=True)

    # fig = plt.figure()


    # ax1 = fig.add_subplot(211)
    # ax1.plot(np.abs(FFT))
    # ax1.plot(magnitude)

    # ax2 = fig.add_subplot(212)
    # ax2.plot(np.fft.ifft(FFT))

    # plt.show()



if __name__ == '__main__':
    main()