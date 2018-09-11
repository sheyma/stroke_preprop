import os, sys
from nilearn import masking
import numpy as np
import h5py
import numexpr as ne

#### Step 1 #### 
#subject_list = ['hc01_d00', 'hc02_d00']
#nameOUT      = 'firsttwo'
# cond  = 'yes' or 'no'

cond = sys.argv[1]

if cond == 'yes':
    fname    = sys.argv[2]
    nameOUT  = sys.argv[3]
    data_in    = '/data/pt_mar006/subjects'
    data_out   = '/data/pt_mar006/newtmp'
    with open(fname) as f:
        content = f.readlines()
        subject_list = [x.strip('\n') for x in content]
    print subject_list
    
    i = 0
    for subject_id in subject_list:
    
        image_rest = os.path.join(data_in, subject_id, 
                                  'preprocessed/func', 
                                  'rest_preprocessed2mni_sm.nii.gz') 
        image_mask = os.path.join('/data/pt_mar006/newtmp',
                                  'gm_prob_mni3_ave_rest.nii.gz')
        t_series   = masking.apply_mask(image_rest, image_mask)
        t_series   = t_series.T
        fc         = np.corrcoef(t_series)
        fcbinar    = np.ones(fc.shape)

        mynanidx          = np.where(np.isnan(fc) == True)
        fc[mynanidx]      = 0
        fcbinar[mynanidx] = 0
        
        if i == 0:
            SUM      = fc
            SUMBINAR = fcbinar
        else:
            SUM      = ne.evaluate('SUM + fc')
            SUMBINAR = ne.evaluate('SUMBINAR + fcbinar')
        i += 1
        print "DONE... ", subject_id, np.shape(SUM), np.max(SUMBINAR), np.min(SUMBINAR)
    
    sumout  = os.path.join(data_out, nameOUT + '.h5')
    h       = h5py.File(sumout, 'w')
    h.create_dataset("data", data = SUM)
    h.close()
    
    binout = os.path.join(data_out, nameOUT + 'binary.h5')
    k      = h5py.File(binout, 'w')
    k.create_dataset("data", data = SUMBINAR)
    k.close()

#### Step 2 #### average...
if cond == 'no':
    chopped_list = ['/data/pt_mar006/newtmp/firstfive.h5',
                '/data/pt_mar006/newtmp/secondfive.h5',
                '/data/pt_mar006/newtmp/thirdfive.h5',
                '/data/pt_mar006/newtmp/fourthfive.h5',
                '/data/pt_mar006/newtmp/fifthfive.h5',
                '/data/pt_mar006/newtmp/sixththree.h5']
    
    binary_list =  ['/data/pt_mar006/newtmp/firstfivebinary.h5',
                '/data/pt_mar006/newtmp/secondfivebinary.h5',
                '/data/pt_mar006/newtmp/thirdfivebinary.h5',
                '/data/pt_mar006/newtmp/fourthfivebinary.h5',
                '/data/pt_mar006/newtmp/fifthfivebinary.h5',
                '/data/pt_mar006/newtmp/sixththreebinary.h5']
    
    i = 0
    for chopped, binary in zip(chopped_list, binary_list):
    
        print chopped
        
        C_init = h5py.File(chopped, 'r')
        C_data = C_init.get('data')
        C_data = np.array(C_data)
        
        B_init = h5py.File(binary, 'r')
        B_data = B_init.get('data')
        B_data = np.array(B_data)
        
        if i == 0:
            SUM    = C_data
            SUMBIN = B_data 
        else:
            SUM    = ne.evaluate('SUM + C_data')
            SUMBIN = ne.evaluate('SUMBIN + B_data' ) 
        i += 1
    
    print np.shape(SUM), np.max(SUM), np.min(SUM)    
    print np.shape(SUMBIN), np.max(SUMBIN), np.min(SUMBIN)    
    
    ave    = np.divide(SUM, SUMBIN)
    
    print np.max(ave), np.min(ave)
    
    h       = h5py.File('/data/pt_mar006/newtmp/avecorr.h5', 'w')
    h.create_dataset("data", data = ave)
    h.close()
    
    
    



