# OpenFOAM-GUI

Designed a GUI for CFD software OpenFOAM, using the package PyFoam it also enables for easy variation of the given problem with a few clicks of the mouse in the GUI. Some code
is still missing for the GUI but the PyFoam variation is complete. It uses containers to connect to a remote server to make the calculations allowing for low-end hardware to still
succesfully use the software aswell as a website you can connect to. Code and interface is primarily written in Dutch.


# Files 

The main.py file contains de Python code to change te parameters of the Dambreak case, the app.py file combines this functionality with a GUI where you can see the result in a gif format aswell (see below). 
![openfoamfoto](https://user-images.githubusercontent.com/80769012/224371785-13b31f99-defc-40e0-805d-7fb85cd13e22.png)

Some example variations are stored in the cloned-dambreak directories, these are viewable in software like ParaView. Simply open the .foam file in ParaView and choose how you want to view the case. 

Lastly the web directory contains a website version of the GUI using docker containers and the Flask library. 
