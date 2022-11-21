#!/usr/bin/env python
import PIL.Image
import conutils
import time
import os
import shutil
import pickle
import argparse
import glob


# ==Globals==
sDbName = "tmp-"+str(hex(time.time_ns())).split("0x")[-1]+".db"
sTmpDir = "output-"+str(hex(time.time_ns())).split("0x")[-1]


# ==Functions==
def fnGenThumbnail(image, nThumbnailWidth, bSave=False, route=""):
    fResizeFactor = image.size[0]/nThumbnailWidth
    imgThumbnail = image.resize((int(image.size[0]/fResizeFactor),
                                 int(image.size[1]/fResizeFactor)),
                                PIL.Image.Resampling.NEAREST)

    if bSave:
        if route == "":
            return print("EXCEPTION!: no route to save thumbnails")

        if not os.path.isdir(route+sTmpDir):
            os.mkdir(route+sTmpDir)

        if not os.path.isdir(route+sTmpDir+"/thumbnails"):
            os.mkdir(route+sTmpDir+"/thumbnails")

        imgThumbnail.save(route+sTmpDir+
                          "/thumbnails/"+
                          str(fnGeneratePixelmap(image))+'.png')

    return imgThumbnail


def fnGeneratePixelmap(image, route=""):
    if route != "":
        image = fnGenThumbnail(image, 3, True, route)  # 3px
    else:
        image = fnGenThumbnail(image, 3, False)  # 3px

    sPixelmap = ""
    lstPixelSequence = list(image.getdata())
    for lstChannel in lstPixelSequence:
        nTotal = 0
        for nValue in lstChannel:
            nTotal += nValue

        sPixelmap += str(hex(nTotal).lstrip("0x").rstrip("L"))

    return sPixelmap


def fnBuildList(lstFielRoutes, nMaxScan, nTotalFiles=0):
    if (nTotalFiles == 0):
        nTotalFiles = len(lstFileRoutes)

    lstRows = list()
    eta = conutils.ETA(nTotalFiles)

    nId = 0
    for fileRoute in lstFileRoutes:
        sFileName = fileRoute.split(conutils.getNavCharacter())[-1]

        nId += 1

        conutils.fnClear()
        print("Building database...")
        print(str(nId)+"/"+str(nTotalFiles))
        print(conutils.fnRenderProgressBar(nTotalFiles, nId)+" "+eta.fnRenderETA()+"\n")

        eta.fnStart()

        if os.path.isfile(fileRoute):
            image = PIL.Image.open(fileRoute)
            image = image.convert('RGBA')

            lstRows.append((nId, sFileName, fnGeneratePixelmap(image), fileRoute))

            print("Current File: "+ str(sFileName))

            if nId > nMaxScan-1:
                break
        eta.fnUpdate(nId)

    with open(sDbName, 'wb') as database:
        pickle.dump(lstRows, database)

    time.sleep(5)
    return print("Database build!\n\n")


def fnScanFiles(parentRoute, lstFileRoutes):
    if parentRoute[-1] != conutils.getNavCharacter():
        parentRoute += conutils.getNavCharacter()

    nTotalFiles = len(lstFileRoutes)
    eta = conutils.ETA(nTotalFiles)

    fnBuildList(lstFileRoutes, nTotalFiles)
    lstFiles = list()
    with open(sDbName, "rb") as flDb:
        lstFiles = pickle.load(flDb)

    lstRecord = list()
    nIndex = nCopies = nErrors = 0
    for fileRoute in lstFileRoutes:
        sFileName = fileRoute.split(conutils.getNavCharacter())[-1]

        nIndex += 1

        conutils.fnClear()
        print("Scanning files...")
        print("Copies: "+ str(nCopies) +", Errors: "+ str(nErrors))
        print(conutils.fnRenderProgressBar(nTotalFiles, nIndex)+" "+eta.fnRenderETA())
        print("\nCurrent File: "+sFileName)

        eta.fnStart()

        if os.path.isfile(fileRoute):
            image = PIL.Image.open(fileRoute)
            image = image.convert('RGBA')
            sPixelmap = fnGeneratePixelmap(image, parentRoute)

            for lstFileInfo in lstFiles:
                if sFileName == lstFileInfo[1]:  # Name check
                    break

                if sPixelmap == lstFileInfo[2]:
                    if not os.path.isdir(parentRoute+sTmpDir):
                        os.mkdir(parentRoute+sTmpDir)

                    if not os.path.isdir(parentRoute+sTmpDir+conutils.getNavCharacter()+str(lstFileInfo[0])):
                        os.mkdir(parentRoute+sTmpDir+conutils.getNavCharacter()+str(lstFileInfo[0]))

                    if os.path.isfile(lstFileInfo[3]):  # Check if file route in db is a file
                        shutil.move(lstFileInfo[3],
                                    parentRoute+sTmpDir +
                                    conutils.getNavCharacter() +
                                    str(lstFileInfo[0]) +
                                    conutils.getNavCharacter() +
                                    lstFileInfo[1])

                    shutil.move(fileRoute,
                                parentRoute+sTmpDir +
                                conutils.getNavCharacter() +
                                str(lstFileInfo[0]) +
                                conutils.getNavCharacter() +
                                sFileName)

                    nCopies += 1
                    lstRecord.append("\nThere's a copy of this image!\n" +
                                     "Original\n" +
                                     str(lstFileInfo[0]) +" | "+ lstFileInfo[1]+": "+ lstFileInfo[2] +
                                     "\nCopy\n" +
                                     str(nIndex) +" | "+ sFileName+": "+ sPixelmap)
                    break

                # if file_index < 15 or file_index > total_files-16:
                #     Duplicate.saveThumbnail(image) #Make check if thumbs folder exists
                # Duplicate.saveThumbnail(image) #Make check if thumbs folder exists

            image.close()
        else:
            nErrors += 1
            lstRecord.append("\nERROR: This File Was Not Found!\n" +
                             sFileName)

        eta.fnUpdate(nIndex)

    if nCopies > 0 or nErrors > 0:
        for sLine in lstRecord:
            print(sLine)

    return print("Done!\n")


def fnCleanInput(route):
    lstFiles = glob.glob(route)
    lstFormats = ["BMP", "DIB", "EPS", "GIF", "ICNS", "ICO", "IM",
                  "JPG", "JPEG", "MSP", "PCX", "PNG", "PPM", "SGI",
                  "TGA", "TIFF", "WEBP"]
    for file in lstFiles:
        sExt = str(file).split(".")[-1].upper()
        bSupported = False

        for sFormat in lstFormats:
            if sExt == sFormat:
                bSupported = True
                break

        if not bSupported:
            print(f"Found Unsupported file extensions!: .{sExt}\n" +
                  "Will proceed to ignore...")
            del lstFiles[lstFiles.index(file)]
    return lstFiles


# ==Main Program==
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--route', required=True, dest='route')
# TO DO: Add -m max files to scan and -s save thumbnails parameters plus opt -td thumbnail dir par

parentDir = parser.parse_args().route
lstFileRoutes = fnCleanInput(parentDir+"/*.*")

if len(lstFileRoutes) > 0:
    fnScanFiles(parentDir, lstFileRoutes)
    os.remove(sDbName)
