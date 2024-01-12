import math
import numpy as np
import plotly.express as px
import streamlit as st
# from matplotlib import pyplot as plt



def main():

    st.title('Vibration Calculate Tool')

    st.markdown("               ")
    st.markdown("               ")

    SIGMA = 4.0
    ALPHA = 0.2
    Lc = 25

    L = 2000.0
    N = 1000
    NN = int(N/2)

    dz = L/N

    i = np.concatenate([np.linspace(0,N/2,NN+1), np.linspace(-NN+1,-1,NN-1)])

    f = i/(N*dz)
    k = 2*np.pi*f
    PSD = lambda x: (2*3*SIGMA**2*Lc)/(1+(x*Lc)**2)**(0.5+ALPHA)

    magnitude = N*np.sqrt(PSD(k))

    phase = 2*np.pi*np.random.randn(N)
    FFT = magnitude * np.exp(1j*phase)
    
    IFFT = np.fft.ifft(FFT)

    magnitude
    FFT
    IFFT

    # fig = plt.figure()


    # ax1 = fig.add_subplot(211)
    # ax1.plot(np.abs(FFT))
    # ax1.plot(magnitude)

    # ax2 = fig.add_subplot(212)
    # ax2.plot(np.fft.ifft(FFT))

    # plt.show()



if __name__ == '__main__':
    main()