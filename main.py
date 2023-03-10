
from os import path
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from numpy import linspace
import os

def parameterVariatie():
    testnummer = int(input("Geef een testnummer "))

    nieuwe_hoogte_water_notscaled = float(input("Geef een nieuwe hoogte voor het water ")) # moet komen van interface max 3.5
    nieuwe_hoogte_water = 0.146*nieuwe_hoogte_water_notscaled
    nieuwe_hoogte_dijk = float(input("Geef een nieuwe hoogte voor de dijk ")) # max 1.3
    nieuwe_breedte_water_notscaled = float(input("Geef een nieuwe breedte voor het water ")) # max 4 
    nieuwe_breedte_water = 0.146*nieuwe_breedte_water_notscaled
    verschuiving = float(input("Geef een verschuiving ")) 
    breedte = float(input("Geef een breedte "))

    templateCase = SolutionDirectory("damBreak-template", archive=None, paraviewLink=False)
    case = templateCase.cloneCase("cloned-dambreak" + str(testnummer))
    dijk_verschuiven(verschuiving, breedte, case)
    edit_height_water(nieuwe_hoogte_water, case)
    edit_dijk_hoogte(nieuwe_hoogte_dijk, case, testnummer) 
    edit_breedte_water(nieuwe_breedte_water, case) 
    os.system("cd cloned-dambreak"+str(testnummer) + "&& mv 0 0.orig")
    os.system("cd cloned-dambreak"+str(testnummer) + "&& ./Allrun")

def edit_height_water(nieuwe_hoogte_water, case):
    Dict = ParsedParameterFile(path.join(case.name,"system","setFieldsDict"))
    Dict["regions"][1]['box'][1][1] = nieuwe_hoogte_water
    Dict.writeFile()

def edit_breedte_water(nieuwe_breedte_water, case):
    Dict = ParsedParameterFile(path.join(case.name,"system","setFieldsDict"))
    Dict["regions"][1]['box'][1][0] = nieuwe_breedte_water
    Dict.writeFile()

def edit_dijk_hoogte(nieuwe_hoogte_dijk, case, testnummer): 
    Dict = ParsedParameterFile(path.join(case.name,"system","blockMeshDict"))
    Dict['vertices'][4][1] = nieuwe_hoogte_dijk
    Dict['vertices'][5][1] = nieuwe_hoogte_dijk
    Dict['vertices'][6][1] = nieuwe_hoogte_dijk
    Dict['vertices'][7][1] = nieuwe_hoogte_dijk
    Dict['vertices'][16][1] = nieuwe_hoogte_dijk
    Dict['vertices'][17][1] = nieuwe_hoogte_dijk
    Dict['vertices'][18][1] = nieuwe_hoogte_dijk
    Dict['vertices'][19][1] = nieuwe_hoogte_dijk
    Dict.writeFile()
    print("File aangepast")
    print(Dict)
    with open("cloned-dambreak" + str(testnummer) + "/system/blockMeshDict", "r") as f:
            lines = f.readlines()
    for i, line in enumerate(lines):
        if line == "blocks\n":
            lines[i+1] = lines[i+1].replace("25", "5")
    with open("cloned-dambreak" + str(testnummer) + "/system/blockMeshDict", "w") as f:
        f.writelines(lines)

def dijk_verschuiven(verschuiving, breedte, case):
    Dict = ParsedParameterFile(path.join(case.name,"system","blockMeshDict"))
    Dict['vertices'][1][0] = Dict['vertices'][1][0] + verschuiving
    Dict['vertices'][2][0] = Dict['vertices'][1][0] + breedte
    Dict['vertices'][5][0] = Dict['vertices'][5][0] + verschuiving
    Dict['vertices'][6][0] = Dict['vertices'][5][0] + breedte
    Dict['vertices'][9][0] = Dict['vertices'][9][0] + verschuiving
    Dict['vertices'][10][0] = Dict['vertices'][9][0] + breedte
    Dict['vertices'][13][0] = Dict['vertices'][13][0] + verschuiving
    Dict['vertices'][14][0] = Dict['vertices'][13][0] + breedte
    Dict['vertices'][17][0] = Dict['vertices'][17][0] + verschuiving
    Dict['vertices'][18][0] = Dict['vertices'][17][0] + breedte
    Dict['vertices'][21][0] = Dict['vertices'][21][0] + verschuiving
    Dict['vertices'][22][0] = Dict['vertices'][21][0] + breedte
    Dict.writeFile()

parameterVariatie()
