#!/home/anl/jing.li/.local/bin/python3
import re,os,argparse
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def msg():
    return '''python3 process.py filename [-h] [-e energy [energy]] '''

parser = argparse.ArgumentParser(usage=msg())
parser.add_argument('filename',metavar = 'f', nargs = 1, type = str, help='filename')
parser.add_argument('-energy','-e',type=float,nargs = '+')
args = parser.parse_args()

data = []

with open(args.filename[0]) as ipf:
    for line in ipf:
        mo = re.search('CALCULATED AND EXPERIMENTAL YIELDS',line)
        if mo :
            mo = re.search(r'\b[0-9]{1,2}\b',line)
            ipf.readline() #skip empty line
            str1 = ipf.readline() # skip instrcution line
            while True :
                str1 = ipf.readline()
                if str1 == '\n' :
                    break
                ldata = []
                ldata.append(mo.group())
                str1 = str1.split()
                if str1[-1] == '*?!*' :
                    str1.pop(-1)
                ldata+=str1[-5:]
                for i,j in enumerate(ldata):
                    try:
                        ldata[i] = float(j)
                    except:
                        print(ldata[i].split('+'))
                        ldata[i] = float(ldata[i].split('+')[0])
                data.append(ldata)

# sort the data according the energy and position

pdtable = pd.DataFrame(data,columns = ['detno','energy','YCal','YExp','diff_per','diff_sig'])

#find out how many energy points are used
grp = pdtable.groupby('energy').groups

drawenergy = []
if not args.energy:
    drawenergy = list(grp.keys())
else:
    for e in args.energy:
        if e in grp.keys():
            drawenergy.append(e)
        else:
            print("{} not in the table".format(e))

drawenergy.sort()
ncol = 3
nrow = (len(drawenergy)+ncol-1)//ncol
nfig = ((ncol*nrow)+6-1)//6
axeslst = []
for i in range(nfig):
    fig,axes = plt.subplots(nrows=2,ncols=ncol,sharex=True,sharey=False)
    axeslst.append(axes)
    plt.tight_layout()


for i, energy in enumerate(drawenergy):
#    pdt1 = pdtable[pdtable['energy']==energy ]
#    pdt1 = pdt1[pdt1['detno']!=1]
    pdt1 = pdtable.loc[ grp[energy] ]
    pdt1 = pdt1[pdt1.detno!=1] # get rid of detno1
    ax1 = pdt1.plot('detno','YCal', kind='scatter',label='YCal',title=str(energy),ax=axeslst[i//6][np.unravel_index(i%6,axes.shape)],sharex=axeslst[0][0,0])
    ax2 = pdt1.plot('detno','YExp', kind='scatter',label='YExp',ax = ax1,color='r',marker='x')
    ax1.ticklabel_format(style='sci',axis='y',scilimits=(0,0))
    ax1.set_ylabel('Yields')
    
    ax3 = ax1.twinx()
    ax3.tick_params(axis='y',labelcolor='g')
    uplimit = pdtable[pdtable.detno!=1]['diff_sig'].abs().max()+2
    dolimit = -uplimit
    ax3.set_ylim(dolimit,uplimit)
    ax4 = pdt1.plot('detno','diff_sig',kind='scatter',label='diff_sig',ax=ax3,color='g',marker='+',s=44)

    scas, labels = ax1.get_legend_handles_labels()
    scas2,labels2 = ax3.get_legend_handles_labels()
    ax1.legend(scas+scas2,labels+labels2)
    ax3.get_legend().remove()
    ax3.set_xlabel('detno')

print(pdtable)
plt.show()
