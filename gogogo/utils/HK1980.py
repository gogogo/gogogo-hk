"""
   Convertion between HK1980 grid reference system and WGS84
 
   (Ported from the PHP code write by Abel Cheung)
"""
import math

M_PI_180 = 0.0174532925199432957692369076849

def wgs84_to_hk1980 (lat,lon,mode=2):
	"""
	  Converts HK1980 data to WGS84 data
	 
	  @param int mode 1 = Hayford, 2 = WGS84
	  @return A tuple of HK1980 grid reference system (North , East )
	"""

	assert(mode == 1 or mode == 2 )

	assert( lat >= 22 and lat < 23)

	assert( lon >= 113 and lon < 115) 

	if mode == 1:
		d4 = 22.312133333333335 * M_PI_180
		d5 = 114.17855555555556 * M_PI_180
	else:
		d4 = 22.310602777777778 * M_PI_180;
		d5 = 114.1810138888889 * M_PI_180;

	d6 = lat * M_PI_180;
	d7 = lon * M_PI_180;

	d8 = SMER (mode, 0, d4);
	d9 = SMER (mode, 0, d6);

	(d34, d35) = RADIUS (mode, d6);

	d10 = (d7 - d5) * math.cos (d6);
	d11 = math.tan (d6);
	d12 = pow (d11, 2);
	d13 = pow (d11, 4);
	d14 = pow (d11, 6);

	d15 = d35 / d34;
	d16 = pow (d15, 2);
	d17 = pow (d15, 3);
	d18 = pow (d15, 4);

	d19 = d9 - d8;

	d20 = (d35 / 2) * pow (d10, 2) * d11;
	d21 = (d20 / 12) * pow (d10, 2) * (d16 * 4 + d15 - d12);
	d22 = (d21 / 30) * pow (d10, 2);
	d22 *=   d18 * (88 - d12 * 192) \
		- d17 * (28 - d12 * 168) \
		+ d16 * (1 - d12 * 32) \
		- d15 * d12 * 2 \
		+ d13;
	d23 = d22 / 56 * pow (d10, 2) \
		* (1385 - 3111 * d12 + d13 * 543 - d14);
	d24 = d35 * d10;
	d25 = d24 / 6  * pow (d10, 2);
	d26 = d25 / 20 * pow (d10, 2);
	
	d27 = d26 / 42 * pow (d10, 2); 
	# The original line from Abel's code should be 
	#  d27 = d27 / 42 * pow (d10, 2);

	d25 *= d15 - d12;
	d26 *= d17 * 4 * (1 - d12 * 6) \
		+ d16 * (1 + d12 * 8) \
		- d15 * d12 * 2 + d13;
	d27 *= 61 - d12 * 479 + d13 * 179 - d14;

	d36 = d19 + d20 + d21 + d22 + d23 + 819069.80000000005;
	d37 = d24 + d25 + d26 + d27 + 836694.05000000005;

	if mode == 2:
		d28 = d36;
		d29 = d37;
		d30 = 0.99999983729999997;
		d31 = -2.7858E-005;

		d36 = (d28 * d30 - d29 * d31) - 23.098331000000002;
		d37 = (d28 * d31 + d29 * d30) + 23.149764999999999;

	north = d36;
	east = d37;

	return (north , east)

def hk1980_to_wgs84 (north,east,mode=2):
	"""
	 Converts HK1980 data to WGS84 data
	 
	 @param mode 1 = Hayford, 2 = WGS84
	 @return A tuple of (lat,lon)
	"""
	assert(mode == 1 or mode == 2 )	

	d1 = north;
	d2 = east;

	if mode == 1:
		d4 = 22.312133333333335 * M_PI_180
		d5 = 114.17855555555556 * M_PI_180
	else:
		d4 = 22.310602777777778 * M_PI_180;
		d5 = 114.1810138888889 * M_PI_180;

	if (mode == 2):
		d6 = 1.0000001619000001;
		d7 = 2.7858E-05;
		d8 = 23.098979;
		d9 = -23.149125000000002;
		d10 = d6 * d1 - d7 * d2 + d8;
		d11 = d7 * d1 + d6 * d2 + d9;
		d1 = d10;
		d2 = d11;

	d28 = d1 - 819069.80000000005;
	d37 = d2 - 836694.05000000005;
	d12 = 6.8535615239999998;
	d13 = 110736.3925;
	d14 = (math.sqrt (d28 * d12 * 4 + pow (d13, 2)) - d13) / 2 / d12 * M_PI_180;
	d15 = d4 + d14;
	d16 = 0;
	d18 = 0;

	while True:
		d15 += d16;
		d17 = SMER (mode, d4, d15);
		d18 = d28 - d17;
		d39, d41 = RADIUS (mode, d15);
		d16 = d18 / d39;
		if not (abs(d18) > 1E-06):
			break;
	
	(d40, d42) = RADIUS (mode, d15);
	d19 = math.tan (d15);
	d20 = pow (d19, 2);
	d21 = pow (d19, 4);
	d23 = d42 / d40;
	d24 = pow (d23, 2);
	d25 = pow (d23, 3);
	d26 = pow (d23, 4);
	d28 = d37 / d42;
	d38 = pow (d28, 2);
	d29 = d37 / d40 * d28 * d19 / 2;
	d30 = d29 / 12 * d38 * ((9 * d23 * (1 - d20) - 4 * d24) + 12 * d20);
	d31 = d29 / 360 * pow (d38, 2);
	d31 *= 8 * d26 * (11 - 24 * d20) \
		- 12 * d25 * (21 - 71 * d20) \
		+ 15 * d24 * (15 - 98 * d20 + 15 * d21) \
		+ 180 * d23 * (5 * d20 - 3 * d21) \
		+ 360 * d21;
	d32 = d29 / 20160 * pow (d38, 3) * (1385 + 3633 * d20 + 4095 * d21 + 1575 * d20 * d21);
	d44 = d15 - d29 + d30 - d31 + d32;
	d33 = d28 / math.cos (d15);
	d34 = d33 * d38 / 6 * (d23 + 2 * d20);
	d35 = d33 * pow (d38, 2) / 120;
	d35 *= d24 * (9 - 68 * d20) - 4 * d25 * (1 - 6 * d20) + 72 * d23 * d20 + 24 * d21;
	d36 = d33 * pow (d38, 3) / 5040 * (61 + 662 * d20 + 1320 * d21 + 720 * d20 * d21);
	d43 = d5 + d33 - d34 + d35 - d36;
	d44 /= M_PI_180;
	d43 /= M_PI_180;

	lat = d44;
	lon = d43;

	return (lat,lon)

def SMER (mode, d1, d2) :
	"""
	 * @param int mode
	 * @param float $d1
	 * @param float $d2
	"""
	if mode == 1:
		d3 = 6378388
		d4 = 0.0033670033670033669
	else:
		d3 = 6378137
		d4 = 0.0033528106647429845

	d5 = 2.0 * d4 - pow (d4, 2);

	d6 = 1.0 \
		+ 0.75 * d5 \
		+ 0.703125 * pow (d5, 2) \
		+ 0.68359375 * pow (d5, 3);
	d7 = 0.75 * d5 \
		+ 0.9375 * pow (d5, 2) \
		+ 1.025390625 * pow (d5, 3);
	d8 = 0.234375 * pow (d5, 2) \
		+ 0.41015625 * pow (d5, 3);
	d9 = 0.068359375 * pow (d5, 3);

	d10 = d2 - d1;
	d11 = math.sin (d2 * 2) - math.sin (d1 * 2);
	d12 = math.sin (d2 * 4) - math.sin (d1 * 4);
	d13 = math.sin (d2 * 6) - math.sin (d1 * 6);

	d14 = d3 * (1.0 - d5);
	d14 *= (d6 * d10) \
		- (d7 * d11 / 2.0) \
		+ (d8 * d12 / 4.0) \
		- (d9 * d13 / 6.0);

	return d14;


def RADIUS (mode, d1):
	"""
	  @access private
	  @param mode
	  @param d1
	 """
	if (mode == 1):
		d2 = 6378388
		d3 = 0.0033670033670033669
	else:
		d2 = 6378137
		d3 = 0.0033528106647429845

	d4 = d3 * 2 - pow (d3, 2);
	d5 = 1.0 - d4 * pow (math.sin (d1), 2);
	d6 = (d2 * (1.0 - d4)) / pow (d5, 1.5);
	d7 = d2 / math.sqrt (d5);

	return (d6, d7);


if __name__ == "__main__":
	hk1980 = (838477.970,818097.267)
	
	wgs84 = hk1980_to_wgs84(*hk1980)
	print "%s => %s"  % (hk1980 , wgs84)

	print "%s => %s"  % (wgs84 , wgs84_to_hk1980(*wgs84))
	

	

