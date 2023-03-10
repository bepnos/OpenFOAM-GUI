from os import path
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import Vector
from numpy import linspace
import os
from time import sleep

def parameterVariatie():
    testnummer = int(input("Geef een testnummer "))

    verschuiving = float(input("Geef een verschuiving "))
    breedte = float(input("Geef een breedte ")) 

    templateCase = SolutionDirectory("damBreak-template", archive=None, paraviewLink=False)
    case = templateCase.cloneCase("cloned-dambreak" + str(testnummer))
    dijk_verschuiven(verschuiving, breedte,  case, testnummer)
    os.system("cd cloned-dambreak"+str(testnummer) + "&& mv 0 0.orig")
    os.system("cd cloned-dambreak"+str(testnummer) + "&& ./Allrun")


def dijk_verschuiven(verschuiving, breedte, case, testnummer):
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
    print("File aangepast")
    print(Dict)
    with open("cloned-dambreak" + str(testnummer) + "/system/blockMeshDict", "r") as f:
            lines = f.readlines()
    for i, line in enumerate(lines):
        if line == "blocks\n":
            lines[i+1] = lines[i+1].replace("25", "5")
    with open("cloned-dambreak" + str(testnummer) + "/system/blockMeshDict", "w") as f:
        f.writelines(lines)
parameterVariatie()
