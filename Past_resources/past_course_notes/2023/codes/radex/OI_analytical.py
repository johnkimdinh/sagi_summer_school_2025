#!* This routine is based on Watson & Storey 1980, and adopted from Liseau et al. 2006
#!* One can compute the statistical equilibrium for neutral atoms or ionized atoms, 
#!* by neglecting the absorption and stimulated emission
import numpy as np 
import matplotlib.pyplot as plt
from astropy import constants,log
from scipy.interpolate import interp1d

def solid_angle(FWHM):
   """to compute the solid angle of the beam
   input:
      FWHM: full-width-half-maximum [arcsec]
   output:
      omega: solid angle [sr] <---> equivalent to beam area
   """
   ##Under the assumption that the beam of a telescope can be approximated
   # two-dimensional, elliptical Gaussian function, we can calculate the solid angle of the
   # beam by integrating over that Gaussian:
   #http://herschel.esac.esa.int/twiki/pub/Public/HifiCalibrationWeb/spatial_response_framework_v1.9.pdf
   ##omega = \int exp[− ln2(2θ/θb)**2] \theta d\theta = pi/4ln2 FWHM**2 ~ 1.133FWHM**2 [degree**2]
   #or https://www.atnf.csiro.au/people/Tobias.Westmeier/tools_spherical.php
   ##or omega = \int\int Gauss * da db = 1.133ϑa*ϑb [degree**2]
   ##Here, ϑa and ϑb are the FWHM of the beam’s major and minor axis, respectively
   omega_deg = 1.133 * (FWHM/3600.)**2
   omega_sr  = omega_deg * 3.046e-4
   return omega_sr

#!* Here, we consider only the [OI] transitions
#!* [OI]63um/[OI]145um line ratio

def OI_line_ratio(Tkin, LTE=False, **kwargs):
    #---------------------------------------------------------
    #Inputs: 
    #   name_of_collider: name of colliders (e.g.,H,H2,H or e)
    #   n_coll: number density of the collider
    #Output:
    #   [OI]63um/[OI]145um
    #---------------------------------------------------------

    ##read the Leiden database 
    ## [OI] has 3 fine-structure levels (1,2,3) with E(1)<E(2)<E(3) [P2<P1<P0]
    ## Radiative transitions: P0->P1: 145um (level 3->2)
    ##                        P1->P2: 63um  (level 2->1)
    #Einstein coefficients
    import readspec
    A32=readspec.trans['A3-2']
    A31=readspec.trans['A3-1']
    A21=readspec.trans['A2-1']
    
    #frequencies
    freq32=readspec.trans['freq3-2']
    freq31=readspec.trans['freq3-1']
    freq21=readspec.trans['freq2-1']
    
    if not (LTE):
        try:
            name_of_collider=kwargs['name_of_collider']
            n_coll=kwargs['n_coll']
        except:
            log.error('Input keyword is not correct!')
        
        #collisonal de-excitation coefficients
        Tkin_range =readspec.colls[name_of_collider]['temps']
        C32_range=readspec.colls[name_of_collider]['C3-2']
        try:
            q32=interp1d(Tkin_range,C32_range)(Tkin)
        except:
            log.warning('collission with %s: Tkin=%.2f is out of the range, the last value is adopted'%(name_of_collider,Tkin))
            q32=C32_range[-1] 
        C31_range=readspec.colls[name_of_collider]['C3-1']
        try:
            q31=interp1d(Tkin_range,C31_range)(Tkin)
        except:
            q31=C31_range[-1]
            log.warning('collission with %s: Tkin=%.2f is out of the range, the last value is adopted'%(name_of_collider,Tkin))
        C21_range=readspec.colls[name_of_collider]['C2-1']
        try:
            q21=interp1d(Tkin_range,C21_range)(Tkin)
        except:
            q21=C21_range[-1]
            log.warning('collission with %s: Tkin=%.2f is out of the range, the last value is adopted'%(name_of_collider,Tkin))

        #collisonal excitation coefficients
        factor23=readspec.lev['g3']/readspec.lev['g2']*np.exp(-(readspec.trans['E3']-readspec.trans['E2'])/Tkin)
        q23=q32*factor23

        factor13=readspec.lev['g3']/readspec.lev['g1']*np.exp(-(readspec.trans['E3']-readspec.trans['E1'])/Tkin)
        q13=q31*factor13
        
        factor12=readspec.lev['g2']/readspec.lev['g1']*np.exp(-(readspec.trans['E2']-readspec.trans['E1'])/Tkin)
        q12=q21*factor12

        #constants
        a=n_coll*q12
        b=n_coll*q23*(n_coll*q32-A32)
        c=n_coll*(q23+q21)+A21
        d=n_coll*q23
        e=n_coll*(q32+q31)+A32+A31
        g=n_coll*q23*(n_coll*q32+A32)
        h=q13/q23
        #fractional populations
        f3=n_coll*q23*(n_coll*q12+q13/q23*(n_coll*(q23+q21)+A21))/(e*c-g)#(a+b*c)*d/(e*c-g)
        f2=(n_coll*q12+q13/q23*(n_coll*(q23+q21)+A21))*e/(e*c-b)-h#(a+b*c)*e/(e*c-b) - h
        f1=1.-(f3+f2)
        print(f1,f2,f3)
    else:
        f3 = readspec.lev['g3']*np.exp(-readspec.lev['E3']/Tkin)
        f2 = readspec.lev['g2']*np.exp(-readspec.lev['E2']/Tkin)

    #emissivity/ntot from P0->P1 [erg s−1 cm−3 Hz−1 sr−1]
    I32=constants.h.cgs.value*freq32/4/np.pi * A32 * f3
    #emissivity/ntot from P1->P2 [erg s−1 cm−3 Hz−1 sr−1]
    I21=constants.h.cgs.value*freq21/4/np.pi * A21 * f2

    #we assume two [OI] lines emitted from the same cloud --> specific intensity = int_{cloud depth} Idl
    #unit of the specific intensity is [erg s−1 cm−2 Hz−1 sr−1]
    # convert to flux [erg s-1 cm-2] dnu*I.
    # because we need to average over beam, so don't need to multiple by beam_area (see Eq.2 in Watson & Storey 1980)

    ##Resolving power of ISO (Oberst et al. 2011)
    R63=223 ; FWHM63=87.2
    R145=249; FWHM145=70.0

    ##bandwidth at 63um
    delta_nu63 = readspec.trans['freq2-1'] * 1./R63
    delta_nu145= readspec.trans['freq3-2'] * 1./R145

    Flux63  = delta_nu63  * I21 #* solid_angle(FWHM63) 
    Flux145 = delta_nu145 * I32 #* solid_angle(FWHM145)
    return Flux63/Flux145

def OI_line_ratio_very_thick(Tkin):
    #For a very thick line (tau --> inf), the specific intensity --> Black boddy function
    import readspec
    def bnu(nu,temp):
        bplanck = 1.47455e-47 * nu * nu * nu /(np.exp(4.7989e-11 * nu / temp)-1.e0 + 1.e-290)
        return bplanck
    ##Resolving power of ISO (Oberst et al. 2011)
    R63=223 ; FWHM63=87.2
    R145=249; FWHM145=70.0

    ##bandwidth at 63um
    delta_nu63 = readspec.trans['freq2-1'] * 1./R63
    delta_nu145= readspec.trans['freq3-2'] * 1./R145

    ##dnuInu
    Flux63  = delta_nu63  * bnu(readspec.trans['freq2-1'],Tkin) #]* solid_angle(FWHM63)
    Flux145 = delta_nu145 * bnu(readspec.trans['freq3-2'],Tkin) #* solid_angle(FWHM145)
    return Flux63/Flux145

if __name__=='__main__':
    fig=plt.figure(figsize=(6,7))
    name_of_colliders=['o-H2','H'];ls=[':','--','-.','-'];color=['blue','magenta','green','black']
    n_coll_range = [1e4,1e5]
    Tkin_range   = np.logspace(1,3.8,1000)
    j=0
    lines=[]
    for name_of_collider in name_of_colliders:
        first_legend=True
        for n_coll in n_coll_range:
            ratio=np.zeros(len(Tkin_range))
            for i,Tkin in enumerate(Tkin_range):
                #if name_of_collider=='p-H2':
                #    ratio[i]=OI_line_ratio(name_of_collider,n_coll/(1+3),Tkin)
                #elif name_of_collider=='o-H2':
                #    ratio[i]=OI_line_ratio(name_of_collider,n_coll/(1+1/3),Tkin)
                #else: 
                ratio[i]=OI_line_ratio(Tkin,name_of_collider=name_of_collider,n_coll=n_coll)
            if first_legend:
                lines+=plt.loglog(Tkin_range,ratio,ls[j],color=color[j],label='collisions with '+name_of_collider)
                first_legend=False
            else:
                plt.loglog(Tkin_range,ratio,ls[j],color=color[j])
        j=j+1
        #plt.legend(name_of_colliders)
    labels = [l.get_label() for l in lines]
    plt.legend(lines, labels,fontsize=17)

    #LTE
    ratio_LTE=np.zeros(len(Tkin_range))
    for i,Tkin in enumerate(Tkin_range):
        ratio_LTE[i]=OI_line_ratio(Tkin,LTE=True)
    plt.loglog(Tkin_range,ratio_LTE,'-',color='darkorange',lw=4)

    #Very thick
    ratio_thick=OI_line_ratio_very_thick(Tkin_range)
    plt.loglog(Tkin_range,ratio_thick,'k-',label='optically thick ($\\tau\\rightarrow \\infty$)')
    plt.legend(fontsize=17)
    plt.axhline(y=10,ls='--',color='gray')
    plt.axhline(y=30,ls='--',color='gray')
    #plt.axhline(y=15.85,ls='--',color='black')
    plt.text(28,36,'Observations',va='center',ha='center',fontsize=15)
    plt.text(28,8,'Observations',va='center',ha='center',fontsize=15)
    plt.xlabel('Temperature (K)')
    plt.ylabel('[OI](63$\\,\\mu$m)/[OI](145$\\,\\mu$m)')
    plt.xlim([10,6e3])
    plt.ylim([0.1,200])
    plt.show()
