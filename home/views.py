import os
from django.shortcuts import render
from django.conf import settings
import numpy as np
import stl
import cv2 as cv

# Set your image processing parameters
# MAX_THICK = 2.0
# MIN_THICK = 1.5
# WIDTH = 200
# PX_PER_MM = 4
check = 0

def index(request):
    return render(request, "index.html")

def computeNormal(points):
	direction = np.cross(points[1] - points[0], points[2] - points[0])
	return direction / np.linalg.norm(direction)

def process_image(request):


    
    if request.method == 'POST':
        # Handle the uploaded image
        image = request.FILES['image']
        MAX_THICK = float(request.POST.get('mx_thick'))
        MIN_THICK = float(request.POST.get('mn_thick'))
        WIDTH = float(request.POST.get('wd'))
        PX_PER_MM = float(request.POST.get('px_mm'))

        # MAX_THICK = 2.0
        # MIN_THICK = 1.5
        # WIDTH = 200
        # PX_PER_MM = 4
        img_array = np.asarray(bytearray(image.read()), dtype=np.uint8)
        rawImg = cv.imdecode(img_array, cv.IMREAD_COLOR)
        grayImg = cv.cvtColor(rawImg, cv.COLOR_BGR2GRAY)
        grayImg = cv.resize(grayImg, None, fx=WIDTH*PX_PER_MM/grayImg.shape[1], fy=WIDTH*PX_PER_MM/grayImg.shape[1])
	# grayImg = grayImg[1000:1000]

        maxVal = np.max(grayImg)
        minVal = np.min(grayImg)
        valRange = maxVal - minVal

        thickRange = MAX_THICK - MIN_THICK

        mmPerPx =  WIDTH / (grayImg.shape[1] - 1)

        pixelThicknesses = np.zeros_like(grayImg, dtype=float)

        pixelThicknesses = MAX_THICK - (thickRange * (grayImg - minVal) / valRange)

        numFrontFaces = 2 * (grayImg.shape[0] - 1) * (grayImg.shape[1] - 1)
        numBackFaces = 2 * (grayImg.shape[0] - 1) * (grayImg.shape[1] - 1)
        numSideFaces = 2 * (grayImg.shape[0] - 1)
        numTopBotFaces = 2 * (grayImg.shape[1] - 1)

        numFaces = numFrontFaces + numBackFaces + (numSideFaces * 2) + (numTopBotFaces * 2)
        # print(numFaces)

        cube = stl.mesh.Mesh(np.zeros(numFaces, dtype=stl.mesh.Mesh.dtype))

        verticies = np.zeros((pixelThicknesses.shape[0], pixelThicknesses.shape[1], 3), dtype=float)

        for rowNum in range(pixelThicknesses.shape[0]):
            for colNum in range(pixelThicknesses.shape[1]):
                verticies[rowNum, colNum, :] = np.array([mmPerPx * colNum, -pixelThicknesses[rowNum, colNum], mmPerPx * (grayImg.shape[0] - rowNum)])
            print(rowNum)

        faceCounter = 0

        # print('marker')

        # Front
        for rowNum in range(pixelThicknesses.shape[0] - 1):
            for colNum in range(pixelThicknesses.shape[1] - 1):
                cube.vectors[faceCounter, 0] = verticies[rowNum, colNum]
                cube.vectors[faceCounter, 1] = verticies[rowNum, colNum + 1]
                cube.vectors[faceCounter, 2] = verticies[rowNum + 1, colNum + 1]
                cube.normals[faceCounter] = computeNormal(cube.vectors[faceCounter])
                faceCounter += 1
                cube.vectors[faceCounter, 0] = verticies[rowNum + 1, colNum + 1]
                cube.vectors[faceCounter, 1] = verticies[rowNum + 1, colNum]
                cube.vectors[faceCounter, 2] = verticies[rowNum, colNum]
                cube.normals[faceCounter] = computeNormal(cube.vectors[faceCounter])
                faceCounter += 1

                cube.vectors[faceCounter, 0] = [verticies[rowNum, colNum][0], 0, verticies[rowNum, colNum][2]]
                cube.vectors[faceCounter, 1] = [verticies[rowNum, colNum + 1][0], 0, verticies[rowNum, colNum + 1][2]]
                cube.vectors[faceCounter, 2] = [verticies[rowNum + 1, colNum + 1][0], 0, verticies[rowNum + 1, colNum + 1][2]]
                cube.normals[faceCounter] = [0,1,0]
                faceCounter += 1
                cube.vectors[faceCounter, 0] = [verticies[rowNum + 1, colNum + 1][0], 0, verticies[rowNum + 1, colNum + 1][2]]
                cube.vectors[faceCounter, 1] = [verticies[rowNum + 1, colNum][0], 0, verticies[rowNum + 1, colNum][2]]
                cube.vectors[faceCounter, 2] = [verticies[rowNum, colNum][0], 0, verticies[rowNum, colNum][2]]
                cube.normals[faceCounter] = [0,1,0]
                faceCounter += 1
            print(rowNum)

        # Top
        for colNum, _ in enumerate(pixelThicknesses[0,0:-1]):
            verticies = np.zeros((4,3), dtype=float)
            verticies[0,:] = np.array([mmPerPx * (colNum), -pixelThicknesses[0, colNum], mmPerPx * grayImg.shape[0]])
            verticies[1,:] = np.array([mmPerPx * (colNum + 1), -pixelThicknesses[0, colNum + 1], mmPerPx * grayImg.shape[0]])
            verticies[2,:] = np.array([mmPerPx * (colNum + 1), 0, mmPerPx * grayImg.shape[0]])
            verticies[3,:] = np.array([mmPerPx * (colNum), 0, mmPerPx * grayImg.shape[0]])

            for i in range(2):
                cube.vectors[faceCounter, 0] = verticies[(i * 2)]
                cube.vectors[faceCounter, 1] = verticies[((i * 2) + 1) % 4]
                cube.vectors[faceCounter, 2] = verticies[((i * 2) + 2) % 4]
                cube.normals[faceCounter] = [0,0,1]
                faceCounter += 1

        # Bottom
        for colNum, _ in enumerate(pixelThicknesses[-1,0:-1]):
            verticies = np.zeros((4,3), dtype=float)
            verticies[0,:] = np.array([mmPerPx * (colNum), -pixelThicknesses[-1, colNum], 1])
            verticies[1,:] = np.array([mmPerPx * (colNum + 1), -pixelThicknesses[-1, colNum + 1], 1])
            verticies[2,:] = np.array([mmPerPx * (colNum + 1), 0, 1])
            verticies[3,:] = np.array([mmPerPx * (colNum), 0, 1])

            for i in range(2):
                cube.vectors[faceCounter, 0] = verticies[(i * 2)]
                cube.vectors[faceCounter, 1] = verticies[((i * 2) + 1) % 4]
                cube.vectors[faceCounter, 2] = verticies[((i * 2) + 2) % 4]
                cube.normals[faceCounter] = [0,0,-1]
                faceCounter += 1

        # Left
        for rowNum, _ in enumerate(pixelThicknesses[0:-1,0]):
            verticies = np.zeros((4,3), dtype=float)
            verticies[0,:] = np.array([0, -pixelThicknesses[rowNum, 0], mmPerPx * (grayImg.shape[0] - rowNum)])
            verticies[1,:] = np.array([0, -pixelThicknesses[rowNum + 1, 0], mmPerPx * (grayImg.shape[0] - (rowNum + 1))])
            verticies[2,:] = np.array([0, 0, mmPerPx * (grayImg.shape[0] - (rowNum + 1))])
            verticies[3,:] = np.array([0, 0, mmPerPx * (grayImg.shape[0] - rowNum)])

            for i in range(2):
                cube.vectors[faceCounter, 0] = verticies[(i * 2)]
                cube.vectors[faceCounter, 1] = verticies[((i * 2) + 1) % 4]
                cube.vectors[faceCounter, 2] = verticies[((i * 2) + 2) % 4]
                cube.normals[faceCounter] = [-1,0,0]
                faceCounter += 1

        # Right
        for rowNum, _ in enumerate(pixelThicknesses[0:-1,-1]):
            verticies = np.zeros((4,3), dtype=float)
            verticies[0,:] = np.array([mmPerPx * (grayImg.shape[1] - 1), -pixelThicknesses[rowNum, -1], mmPerPx * (grayImg.shape[0] - rowNum)])
            verticies[1,:] = np.array([mmPerPx * (grayImg.shape[1] - 1), -pixelThicknesses[rowNum + 1, -1], mmPerPx * (grayImg.shape[0] - (rowNum + 1))])
            verticies[2,:] = np.array([mmPerPx * (grayImg.shape[1] - 1), 0, mmPerPx * (grayImg.shape[0] - (rowNum + 1))])
            verticies[3,:] = np.array([mmPerPx * (grayImg.shape[1] - 1), 0, mmPerPx * (grayImg.shape[0] - rowNum)])

            for i in range(2):
                cube.vectors[faceCounter, 0] = verticies[(i * 2)]
                cube.vectors[faceCounter, 1] = verticies[((i * 2) + 1) % 4]
                cube.vectors[faceCounter, 2] = verticies[((i * 2) + 2) % 4]
                cube.normals[faceCounter] = [1,0,0]
                faceCounter += 1

        print(faceCounter, cube.vectors.shape[0])
        stl_file_path = os.path.join(settings.MEDIA_ROOT, 'tactile.stl')
        cube.save(stl_file_path)  # Assuming `cube` is the STL object

        # Construct the file URL relative to the media root
        stl_file_url = os.path.join(settings.MEDIA_URL, 'tactile.stl')

        # Pass the file URL to the template for rendering
        check = 1
        context = {'stl_file_url': stl_file_url, 'check' : check}
        return render(request, 'upload.html', context)


    return render(request, 'upload.html')

def text(request):
        return render(request, "textBraille.html") 
