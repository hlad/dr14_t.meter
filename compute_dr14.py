# dr14_t.meter: compute the DR14 value of the given audiofiles
#Copyright (C) 2011  Simone Riva
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from numpy  import *
import math
import numpy


def dr_rms( y ) :
	n = y.shape
	rms = numpy.sqrt( 2 * sum( y**2 , 0 ) / n[0] ) 
	return rms 
	
def u_rms( y ) :
	n = y.shape
	rms = numpy.sqrt( sum( y**2 , 0 ) / n[0] ) 
	return rms 

def decibel_u( y , ref ) :
	return 20 * numpy.log10( y / ref )

def compute_dr14( Y , Fs ) :
	s = Y.shape
	ch = s[1]
	
	if Fs == 44100:
		delta_fs = 60 
	else:
		delta_fs = 0 	
	
	block_time = 3 
	cut_best_bins = 0.2
	block_samples = block_time * ( Fs + delta_fs )
	
	seg_cnt = math.floor( s[0] / block_samples ) + 1
	
	if seg_cnt < 3:
		return ( 0 , -100 , -100 )
	
	curr_sam = 0 
	rms = zeros((seg_cnt,ch))
	peaks = zeros((seg_cnt,ch))
	
	for i in range(seg_cnt - 1):
		r = arange(curr_sam,curr_sam+block_samples)
		rms[i,:] = dr_rms( Y[r,:] ) 
		peaks[i,:] = numpy.max( numpy.abs( Y[r,:] ) , 0 ) 
		curr_sam = curr_sam + block_samples
	
	i = seg_cnt - 1 ;
	r = arange( curr_sam,s[0] )
	
	#print( s )
	#print( curr_sam )
	#print ( r )
	
	if r.shape[0] > 0:
		rms[i,:] = dr_rms( Y[r,:] )
		peaks[i,:] = numpy.max( numpy.abs( Y[r,:] ) , 0 )
	
	peaks = numpy.sort( peaks , 0 )
	rms = numpy.sort( rms , 0 )
	
	n_blk = int( floor( seg_cnt * cut_best_bins ) )
	if n_blk == 0:
		n_blk = 1
		
	r = arange(seg_cnt-n_blk,seg_cnt) 
	
	rms_sum = numpy.sum( rms[r,:]**2 , 0 ) 
	
	ch_dr14 = -20*numpy.log10( numpy.sqrt( rms_sum / n_blk ) * 1/peaks[seg_cnt-2,:] )
	
	err_i = (rms_sum < 1/(2**24))
	ch_dr14[err_i] = 0 ;
		
	dr14 = round( numpy.mean( ch_dr14 ) )
	
	dB_peak = decibel_u( numpy.max( peaks ) , 1 )
	
	y_rms = u_rms( Y ) 
	dB_rms = decibel_u( numpy.sum( y_rms ) , 1 )
	
	
	return ( dr14 , dB_peak , dB_rms )
	
