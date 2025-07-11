import numpy as np 
from sys import exit
import os, re

##------------------------------constant-----------------------------##
from astropy import constants
h = constants.h.cgs.value
kB= constants.k_B.cgs.value
c = constants.c.cgs.value

def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

# Read database file
# path = os.getcwd()
# q          = np.genfromtxt(path+'/inputs.inp',skip_header=0,dtype=None,names=['params'],\
#                           comments='!',usecols=(0),encoding='utf=8')
# params     = q['params']
# line_input       = params[4]
# mol_name = re.search(r'(?<=)\w+',line_input).group(0)
# path_spec  =  path + '/moldata/'
# filename = path_spec + mol_name.casefold()+'.dat'
filename = 'oatom@lique.dat'
mol_data={}
lev={}
trans={}
colls={}
#colls_reverse={}
read_first=True;store_first=True

with open(filename,'r') as f:
    lines=f.readlines()
    if (read_first):
        for k,kline in enumerate(lines):
            kline=kline.split()
            #print 'k=',k
            if 'MOLECULE' in kline[0]:
                mol_data['name']=lines[k+1].split()[0]
                continue
            if 'MOLECULAR' in kline[0]:
                mol_data['weight']=eval(lines[k+1].split()[0])
                continue
            if 'LEVELS' in kline:
                mol_data['levs']=eval(lines[k+1].split()[0])
                ilev=k+2
                continue
            if 'TRANSITIONS' in kline:
                #print 'we are here'
                mol_data['trans']=eval(lines[k+1].split()[0])
                itrans=k+2
                continue
            if 'PARTNERS' in kline:
                ##number of collider:
                n_collider=eval(lines[k+1].split()[0])
            if 'COLLISIONS' in kline[0]:
                ##number of collider:
                n_collider=eval(lines[k+1].split()[0])
                n_coll1_trans=eval(lines[k+3].split()[0])
                n_coll1_temps=eval(lines[k+5].split()[0])
                if (store_first):
                    mol_data['collider']={}
                    nom_collider_old=lines[k+1].split()[3]
                    store_first=False
                    icoll1=k+2
                ##endif
                    
                if n_collider ==1:
                    #mol_data['collider']=nom_collider_old
                    #mol_data['collider'].append(nom_collider_old)
                    mol_data['collider'][str(nom_collider_old)]=k+2
                    colls[str(nom_collider_old)]={}
                    #colls_reverse[str(nom_collider_old)]={}
                    first=False
                    #icoll2=1000
                    break
                else:
                    nom_collider_new=lines[k+1].split()[3]
                    #mol_data['collider']='%s,%s'% (nom_collider_old,nom_collider_new)
                    #mol_data['collider'].append(nom_collider_new)
                    mol_data['collider'][str(nom_collider_new)]=k+2
                    colls[str(nom_collider_new)]={}
                    #colls_reverse[str(nom_collider_new)]={}
                    icoll2=k+2
                    continue
                ##endif
            ##endif
            read_first=False
        ##endloop
    ##endif
f.close()

##initialize
trans['E1']=0.0
trans['range_up']=[]
trans['range_low']=[]
lev['levels']=[]
for i,line in enumerate(lines):
    ##---------------------------
    ## Save to lev
    ##---------------------------
    if i<=itrans:
        cols=lines[i].split()
        try:
            lev['g'+str(eval(cols[0]))]=eval(cols[2])
            lev['E'+str(eval(cols[0]))]=eval(cols[1])*h*c/kB
            lev['levels'].append(eval(cols[0]))
        except:
            continue
    ##endif
    ##---------------------------
    ## Save to trans
    ##---------------------------
    icolls=sorted(mol_data['collider'].values())
    icoll_min=min(icolls)
    if (i>itrans) and (i<icoll_min-1):
        cols=lines[i].split()
        try:
            up=cols[1]; low=cols[2]
            #print up,low
            trans['E'+up]=eval(cols[-1])
            trans['A'+up+'-'+low]=eval(cols[3])
            trans['up']=eval(up)
            trans['low']=eval(low)
            trans['range_up'].append(eval(up))
            trans['range_low'].append(eval(low))
            trans['freq'+up+'-'+low]=eval(cols[4])*1e9
            trans['B'+up+'-'+low]=c*c/(2.*h*trans['freq'+up+'-'+low]**3.) * trans['A'+up+'-'+low]
            trans['B'+low+'-'+up]=lev['g'+up]/lev['g'+low] * trans['B'+up+'-'+low]
        except:
            continue
    ##endif
##endloop

##--------------------------
## Save to colls
##--------------------------
icolls=sorted(mol_data['collider'].values())
for icoll in icolls:
    name_collider=getKeysByValue(mol_data['collider'],icoll)[0]
    print ('********')
    print ('icoll',icoll)
    for i in range(icoll,len(lines)):
        line = lines[i].split()
        if (i>icoll+4) and (i<icoll+6):
            cols=lines[i].split()
            try:
                print ('we are at temps with', str(name_collider))
                colls[name_collider]['temps']=np.array([eval(cols[ii]) for ii in range(len(cols))])
            except:
                continue
        ##endif
        if (i>icoll+6):
            #print 'we are at C with', str(name_collider)
            cols=lines[i].split()
            #try:
            #print 'we are here'
           # print 'i=',i
            #exit(0)
            try:
                #up=cols[0]; low=cols[1]
                #colls[name_collider]['C'+up+'-'+low]=array([eval(cols[ii]) for ii in range(len(cols))])[2:]
                up=cols[1]; low=cols[2]
                colls[name_collider]['C'+up+'-'+low]=np.array([eval(cols[ii]) for ii in range(len(cols))])[3:]
                # conversion_factor=lev['g'+up]/lev['g'+low]*np.exp(-(trans['E'+up]-trans['E'+low])/Tn)
                # #conversion_factor=lev['g'+up]/lev['g'+low]*exp(-(lev['E'+up]-lev['E'+low])/Tn)
                # #colls_reverse[name_collider]['C'+low+'-'+up]=colls[name_collider]['C'+up+'-'+low]*conversion_factor
                # colls[name_collider]['C'+low+'-'+up]=colls[name_collider]['C'+up+'-'+low]*conversion_factor
            except:
                pass
        ##endif
        if 'COLLISIONS' in line[0]:
            print ('we are in break')
            print ('try=',i)
            break
        ##endif
    ##endloop
##endloop
