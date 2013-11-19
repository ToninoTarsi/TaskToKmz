###########################################################################
#	 TaskToKmz
#	 Copyright 2013 by Tonino Tarsi <tony.tarsi@gmail.com>
#   
#	 Please refer to the LICENSE file for conditions 
#	 Visit http://www.vololiberomontecucco.it
# 
##########################################################################

import os
import string
import random


################################# modify below #####################################


inIGCDir = "./igc"
outFile = "./task.kml"
taskName = "Task"
modelscale = "5"
crateFlyForAllPilots = True
startTime = "1230"  # or use "none"
endTime = "1800"
pilots2follow = ["CHRISTIAN CIECH","ALESSANDRO PLONER","EDOARDO GIUDICEANDREA"] # Ingnored if crateFlyForAllPilots
flySpeed = 8
tilt = 75
min_distance = 1500
max_distance = 2500
split_tout_time = 1
heigth_offset = 100

################################# Do not modify below #####################################


def isAfterStart(theTime,startTime):
	r = ( int(theTime[0:2])*60+int(theTime[3:4]) ) -  ( int(startTime[0:2])*60+int(startTime[3:4]) )
	if ( r >= 0):
		return True
	else:
		return False

class gpsPoint(object):
	def __init__(self, t,y,x,h):
		code = x[7]
		deg = x[0:2]
		pri = x[2:4]
		dec  = x[4:7]
		dx = float(deg) + (float(pri)+ float(dec)/1000) /60
		if ( code == "W"):
			dx = -dx
		self.x = dx
		
		
		code = y[7]
		deg = y[0:2]
		pri = y[2:4]
		dec  = y[4:7]
		dy = float(deg) + (float(pri)+ float(dec)/1000) /60		
		if ( code == "S"):
			dx = -dx
		self.y = dy
		
		self.h = float(h)+heigth_offset
		self.t = t

class igcClass(object):
	def __init__(self, filename):
		self.filename = filename
		self.PilotName = None
		self.date = None
		self.day =  None
		self.year =  None
		fo = open(filename, "r")

		while ( True ):
			line = fo.readline()
			#print line
			if ( line.split(" ")[0] == "HOPLTPILOT:" or  line.split(" ")[0] == "HFPLTPILOT:") :
				self.PilotName = line[12:len(line)-1]
			if line[0:5] == "HFDTE":
				self.date = line[5:]
				self.day = line[5:7]
				self.month = line[7:9]
				self.year = line[9:11]
			if ( line.split(" ")[0] == "HOSITSite:" or line.split(" ")[0][0] == 'B'):
				break
		
		fo.close()
		
		
	def GetPoints(self):
		fo = open(self.filename, "r")
		while ( True ):
			line = fo.readline()
			if ( line.split(" ")[0] == "HOSITSite:" or line.split(" ")[0][0] == 'B' ):
				break
		line = fo.readline()
		code = line[0]
		listGPS = []
		
		while ( code == "B" ):
			theTime = line[1:7]
			if isAfterStart(theTime,startTime):
				listGPS.append(gpsPoint(line[1:7],line[7:15],line[16:24],line[26:30]))
			line = fo.readline()
			code = line[0]

		fo.close()
		return listGPS
				
		
		

whitelist = ['.igc']
contents = os.listdir(inIGCDir)
igcfilelist = []
for filename in contents:
	if os.path.splitext( filename )[1]  in whitelist:
		igcfilelist.append(inIGCDir + "/" +filename)
		

listigc = []
for igcfile  in igcfilelist:
	igc = igcClass(igcfile)
	listigc.append(igc)
	

outfo = open(outFile,"w")	

template1 = string.Template("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>$TaskName</name>
	<open>1</open>
	""")

d = dict(TaskName=taskName)
outfo.write(template1.safe_substitute(d))



i = 0
for pilot in listigc:
	x = random.randint(0, 16777215)
	labelcolor =  "FF%x" % x
	trackcolor = "7F%x" % x
	templateStyle = string.Template("""<StyleMap id="StyleMapID$i">
		<Pair>
			<key>normal</key>
			<styleUrl>#style$i</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#hl</styleUrl>
		</Pair>
	</StyleMap>
	<Style id="style$i">
		<IconStyle>
			<Icon>
			</Icon>
		</IconStyle>
		<LabelStyle>
			<color>$labelcolor</color>
			<scale>0.4</scale>
		</LabelStyle>
		<LineStyle>
			<color>$trackcolor</color>
			<width>0.5</width>
		</LineStyle>
	</Style>
	""")
	
	d = dict(i=i)
	d.update(labelcolor=labelcolor)
	d.update(trackcolor=trackcolor)

	outfo.write(templateStyle.safe_substitute(d))
			
	i = i + 1		

outfo.write("""	<Folder>
		<name>Pilots</name>
		<open>1</open>
		""")

i = 0
for pilot in listigc:			
	print pilot.PilotName
				
	template = string.Template("""<Placemark>
			<name>$pilotName</name>
			<styleUrl>#style$i</styleUrl>
			""") 
	
	d = dict(i=i)
	d.update(pilotName=pilot.PilotName)			
	outfo.write(template.safe_substitute(d))
			
	outfo.write("""			<gx:Track>
				<altitudeMode>absolute</altitudeMode>""")

	points = pilot.GetPoints()
	for point in points:
		when = "            <when>20"+pilot.year+"-"+pilot.month+"-"+pilot.day+"T"+point.t[0:2]+":"+point.t[2:4]+":"+point.t[4:6]+"Z</when>"
		outfo.write(when+"\n")
	
	for point in points:
		when = "           <gx:coord>%.6f %.6f %.0f</gx:coord>" % (point.x,point.y,point.h)
		outfo.write(when+"\n")
	

	
	template = string.Template("""				<Model id="model_3">
					<altitudeMode>relativeToGround</altitudeMode>
					<Location id="model_3">
						<longitude>$x</longitude>
						<latitude>$y</latitude>
						<altitude>$h</altitude>
					</Location>
					<Orientation>
						<heading>360</heading>
						<tilt>0</tilt>
						<roll>0</roll>
					</Orientation>
					<Scale>
						<x>$s</x>
						<y>$s</y>
						<z>$s</z>
					</Scale>
					<Link>
						<href>files/hg.dae</href>
					</Link>
					<ResourceMap>
					</ResourceMap>
				</Model>
			</gx:Track>
		</Placemark>
		""")
	
	
	d = dict(s=modelscale)
	d.update(x=points[0].x)	
	d.update(y=points[0].y)	
	d.update(h=points[0].h)			
	outfo.write(template.safe_substitute(d))	
	
	i = i + 1	

outfo.write("</Folder>")

outfo.write("""	<Folder>
		<name>fly</name>
		<open>1</open>
		""")


# #########################    Create tour

for pilot in listigc:			
	if pilot.PilotName in pilots2follow or crateFlyForAllPilots :
		print "Creating tour for" + pilot.PilotName
		outfo.write("""<gx:Tour>
			<name>"""+pilot.PilotName+"""</name>
			<gx:Playlist>""")
		
		points = pilot.GetPoints()
		i = 0
		hp = 0
		heading = random.randint(0, 360)
		distance  = random.randint(min_distance,max_distance)
		distance_step = 50
		for point in points:
			if ( i % 10 == 0  ):
				if ( i % 20 or True) :
					distance = distance + distance_step
					if   ( distance > max_distance ) :
						 distance_step = - distance_step
					if ( distance < min_distance ) :
						 distance_step = - distance_step
				if ( i % 5 == 0  ):
					heading = heading + 5 
					if ( heading > 360):
						heading = 0
				bgn="20"+listigc[0].year+"-"+listigc[0].month+"-"+listigc[0].day+"T"+points[0].t[0:2]+":"+points[0].t[2:4]+":"+points[0].t[4:6]+"Z"
				end="20"+pilot.year+"-"+pilot.month+"-"+pilot.day+"T"+point.t[0:2]+":"+point.t[2:4]+":"+point.t[4:6]+"Z"
				
				h = int(point.t[0:2]) * 3600 + int(point.t[2:4])*60 + int(point.t[4:6])
				if ( hp == 0):
					timetofly = 1
				else:
					timetofly = ( h - hp ) / flySpeed
				hp = h
				
				template = string.Template("""			<gx:FlyTo>
					<gx:duration>$timetofly</gx:duration>
					 <gx:flyToMode>smooth</gx:flyToMode>
					<LookAt>
						<TimeSpan>
							<begin>$bgn</begin>
							<end>$end</end>
						</TimeSpan>
						<longitude>$x</longitude>
						<latitude>$y</latitude>
						<altitude>$h</altitude>
						<heading>$heading</heading>
						<tilt>$tilt</tilt>
						<range>$distance</range>
						<altitudeMode>absolute</altitudeMode>
					</LookAt>
				</gx:FlyTo>""")
				
				d = dict(bgn=bgn)
				d.update(end=end)	
				d.update(x=point.x)	
				d.update(y=point.y)	
				d.update(h=point.h)		
				d.update(timetofly=timetofly)		
				d.update(heading=heading)		
				d.update(tilt=tilt)		
				d.update(distance=distance)		


					
				outfo.write(template.safe_substitute(d))

			i = i + 1
			
		outfo.write("""</gx:Playlist>
			</gx:Tour>""")

outfo.write("""</Folder>
</Document>
</kml>
""")






outfo.close()
print "Done"
	
	