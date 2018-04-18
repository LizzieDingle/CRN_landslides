# Code used to generate outlet CRN concentrations as presented in Dingle et al. (2018) in Earth Surface Dynamics Discussion paper https://doi.org/10.5194/esurf-2017-73
# 


import numpy as np
import math



##Catchment details
Catchment_area = 23000   # in km2
Ganga_catchment_production = 35 # Average surface production rate across catchment in atoms per gram
RockDensity = 2.7 # t/m3
Attenuation = 160 # g/cm2 
BackgroundErosion = 0.6 # in mm/yr 
LandslideErosion = 0.6 #Background erosion in landslide area in mm/yr. Probably best to keep same as BackgroundErosion above!


#Landslide details
AverageLandslideDepth = 2.0 # average depth in metres
LandslideProportion = 0.5  # Proportion of catchment affected by landsliding in %
LandslideSurfaceProduction = 10. #Landslide surface production rate in atoms per gram
Delay = 1 #Used to reflect time taken to evacuate sediment - expressed as 1/time in years - default = 1

#Production rate variation with depth calculated using : SurfaceProductionRate * e^(-rock density*depth/attenuation)  from equation 20 in Niedermann (2002)

##Concentration calculated using: (ProductionRate*Attenuation)/(RockDensity*(ErosionRate + (Attenuation*Decay/RockDensity)))  -- assumes no decay so simplifies to 
## Conc = (ProductionRate*Attenuation)/(RockDensity*ErosionRate) -- taken from Eqn 33 in Niedermann (2002)


# Calculate area and volume of landsliding in m2/m3. Convert to flux in Mt
LandslideArea = (LandslideProportion/100)*Catchment_area*(10**6)  
LandslideVolume = LandslideArea*AverageLandslideDepth

print "Landslide area is..."+str(LandslideArea)+" m2"
print "Landslide volume is..."+str(LandslideVolume)+" m3"

LandslideFlux = (LandslideVolume*RockDensity)/(10**6)  # Landslide mass in Mt

print "Landslide flux is..."+ str(LandslideFlux) +" Mt"

#Calculate average concentration of landslide deposit depending on depth. Assumes no production at depths greater than 2m. At depths between 0 - 2m, production rate decays exponentially which is accounted for here
if AverageLandslideDepth >2:
    LandslideConc2m = ((LandslideSurfaceProduction*0.3)*Attenuation)/(RockDensity*(LandslideErosion/10))  #Assumes no decay with time. The 0.3 comes from some playing around with a spreadsheet...
    LandslideConc = (LandslideConc2m*((LandslideArea*2*RockDensity)/10**6))/LandslideFlux   # LandslideConc gives you concentration averaged across ENTIRE deposit (where at depths >2m we assume no production)
    
else:
    Depth = np.arange(0,(AverageLandslideDepth*100),0.5) 
    Production = []
    UpperConc = []
    for j in Depth:    
        Production.append(LandslideSurfaceProduction*math.exp(-1*RockDensity*j/Attenuation))
    for k in Production:
        UpperConc.append((k*Attenuation)/(RockDensity*(LandslideErosion/10)))
    UpperLandslideConc = sum(UpperConc)/len(UpperConc)  #Gives mean landslide conc in depths <2 m as a function of production rate.
    #UpperLandProportion = UpperLandslideConc/UpperConc[0]
    #print UpperLandProportion 
    
    LandslideConc = UpperLandslideConc
    
print "Landslide conc is..."+ str(LandslideConc) +" atoms/g"   
 

# Background erosion rates and fluxes over the rest of the catchment
BackgroundFlux = ((BackgroundErosion/1000)*((Catchment_area*(10**6)-LandslideArea)*RockDensity)/(10**6))   
BackgroundConc = ((Ganga_catchment_production*Attenuation)/(RockDensity*(BackgroundErosion/10)))

print "Background flux is..."+ str(BackgroundFlux) +" Mt"
print "Background conc is..."+ str(BackgroundConc) +" Mt"


#Mix it all up to get concentration at the outlet...
OutletConc = ((LandslideConc*(LandslideFlux*Delay))+(BackgroundConc*BackgroundFlux))/(BackgroundFlux+(LandslideFlux*Delay))  #Option to reduce landslide flux by number of years expected to flush

print "Outlet conc is..."+ str(OutletConc) +" atoms/g"


#Convert this conc back to an erosion rate? Just playing around here

Erosion = ((Attenuation/RockDensity)*(Ganga_catchment_production/OutletConc))*10  #Quite approximate!

print "Catchment erosion rate is..."+ str(Erosion) + " mm/yr"

AverageFlux = (Erosion/1000)*(Catchment_area*10**6)*RockDensity/(10**6)   #This is based on a catchment average erosion rate based on conc. at the outlet
ActualFlux = BackgroundFlux+(LandslideFlux*Delay)  #This is based on volumetric sediment flux from spatially variable erosion

print "Average Cosmo Flux is "+ str(AverageFlux) + " Mt/yr"
print "Actual Volumetric Flux is "+ str(ActualFlux) + " Mt/yr"