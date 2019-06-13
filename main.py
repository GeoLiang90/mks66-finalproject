#from script import run
import sys, time
from display import *
from Sphere import *
from Vector import *
from Ray import *
from Light import *
from functools import reduce
from Triangle import *
from draw import *
def getColor(ray, objlst, lightlst, numBounces):
    if numBounces <= 0:
        return Vector([0,0,0])
    closest = None
    closestObj = None
    for i in objlst:
        currT = i.isIntersect(ray)
        if closest == None or (currT != None and currT < closest):
            closest = currT
            closestObj = i
    if closest == None:
        return Vector([0,0,0])
    hitColor = Vector([0,0,0])
    intersectPoint = ray.pointAtT(closest)
    reflectedRay = closestObj.getReflected(ray, intersectPoint)
    #Make successive bounces less important based on spectral constants
    colorDecay = Vector([closestObj.cons[1]['red'][2], closestObj.cons[1]['green'][2], closestObj.cons[1]['blue'][2]])
    normal = closestObj.getNormal(intersectPoint)
    if normal.dot(reflectedRay.d) < 0:
        normal *= -1
    for light in lightlst:
        rayToLight = Ray(intersectPoint, (light.pos - intersectPoint))
        if normal.dot(rayToLight.d) < 0:
            continue
        distToLight = rayToLight.d.get_mag()
        rayToLight.d.normalize()
        for obj in objlst: #Check for object hit
            dist = obj.isIntersect(rayToLight)
            if dist != None and dist < distToLight:
                break
        else: #Executed if objects are exhausted without break
            #Phong model
            hitColor += light.calculateColor(distToLight, rayToLight, normal, ray.d, closestObj.cons)
        continue
    return (hitColor + getColor(reflectedRay, objlst, lightlst, numBounces - 1).multComponents(colorDecay))

def scaleColors(screen, newMinComp, newMaxComp = 255):
    maxColorComp = screen[0][0][0] #Max color component ex: [10, 20, 30] -> 30
    minColorComp = maxColorComp
    def getminmax(currminmax, colorComp):
        if colorComp > currminmax[0]:
            currminmax[0] = colorComp
        elif colorComp < currminmax[1]:
            currminmax[1] = colorComp
        return currminmax
    colorCompMinMax = reduce(getminmax, [x for i in screen for j in i for x in j], [maxColorComp, minColorComp])
    if colorCompMinMax[0] == colorCompMinMax[1]: #Solid color screen
        return
    scalar = float(newMaxComp) / (colorCompMinMax[0] - colorCompMinMax[1])
    for y in range(YRES):
        for x in range(XRES):
            screen[y][x] = [int(c * scalar + newMinComp) for c in screen[y][x]]


'''
if len(sys.argv) == 2:
    run(sys.argv[1])
elif len(sys.argv) == 1:
    run(raw_input("please enter the filename of an mdl script file: \n"))
else:
    print "Too many arguments."
'''

zbuff = new_zbuffer(500,500)
screen = new_screen()
color = [ 255, 0, 0 ]
vals = []

#Making the center as a vector allows me to use my overloaded operators
test = Sphere(Vector([250,250,100]),50)
objlst = [test, Sphere(Vector([50, 50, 30]), 20), Sphere(Vector([330, 250, 100]), 30), Sphere(Vector([250, 500, 100]), 70)]
lightlst = [Light(Vector([-500, 250, 0]), Vector([1770000, 1560000, 2170000])),
            Light(Vector([250, 190, 100]), Vector([1190, 1580, 2030])),
            Light(Vector([400, 400, 100]), Vector([25500, 10500, 9700])),
            Light(Vector([750, -250, 100]), Vector([2550000, 2550000, 2550000]))]
# lightlst = [Light(Vector([-500, 250, 0]), Vector([1770000, 1560000, 2170000]))]
# lightlst = [Light(Vector([190, 250, 100]), Vector([119, 158, 203]))]
test0 = Triangle(Vector([100,300,100]),Vector([200,300,100]),Vector([150,450,100]))
temp = []
#add_torus(temp,250,250,100,25,150,50)
add_box(temp,100,350,100,100,100,100)
tmp = new_matrix()
ident(tmp)
matrix_mult(make_rotX(30),tmp)
matrix_mult(make_rotY(-20), tmp)
matrix_mult(tmp,temp)

triangles = []
for x in range(0,len(temp) - 2,3):
    triangles.append(Triangle(Vector(temp[x][:3]),Vector(temp[x + 1][:3]),Vector(temp[x + 2][:3])))

# triangles.append(Triangle( Vector([300, 200, 100]), Vector([250, 300, 100]), Vector([200, 200, 100]) ))

startTime = time.time()

# firedRay = Ray(Vector([250,250,0]), Vector([0,0,1]))
# t = triangles[0].isIntersect(firedRay)
# print(t)
# refl = triangles[0].getReflected(firedRay, firedRay.pointAtT(t))
# print(firedRay)
# print(refl)
def drawNoPerspective():
    for x in range(XRES):
        for y in range(YRES):
            #print(test.isIntersect(z,[250,250,0]))
            firedRay = Ray(Vector([x,y,0]),Vector([0,0,1]))
            #print(test0.isIntersect(firedRay))
            # for obj in objlst:
            #     if obj.isIntersect(firedRay):
            #         plot(screen,zbuff,color,x,y,1)
            colorVector = getColor(firedRay, objlst, lightlst, 5)
            plot(screen,zbuff,colorVector.direction,x,y,1)
    #
    #         ''' Triangle Test
    #         if test0.isIntersect(firedRay):
    #             #print("hit")
    #             plot(screen,zbuff,color,x,y,1)
    #         '''
    #
    #         ''' Testing Some of my stuff IMPORTANT UNCOMMENT THIS PLZ
    #         colorVector = getColor(firedRay, objlst, lightlst, 5)
    #         plot(screen,zbuff,colorVector.direction,x,y,1)
    #         '''

def drawPerspective(ang, useRad = False): #55 degrees is human
    if not(useRad):
        if not(ang < 180 and ang > 0):
            print("Invalid view angle")
            return
        ang *= math.pi / 180
    else:
        if not(ang < math.pi and ang > 0):
            print("Invalid view angle")
            return
    midX = XRES/2.
    midY = YRES/2.
    distAway = -1 * (midX / math.tan(ang / 2))
    for x in range(XRES):
        for y in range(YRES):
            # print(test.isIntersect(z,[250,250,0]))
            firedRay = Ray( Vector([midX, midY, distAway]), ( Vector([x, y, 0]) - Vector([250, 250, distAway]) ).normalize() )
            # print(firedRay)
            # print(test0.isIntersect(firedRay))
            # for obj in objlst:
            #     if obj.isIntersect(firedRay):
            #         plot(screen,zbuff,color,x,y,1)
            colorVector = getColor(firedRay, objlst, lightlst, 5)
            plot(screen,zbuff,colorVector.direction,x,y,1)

# drawNoPerspective()
drawPerspective(55)
scaleColors(screen, 0)
print("%f Seconds Elapsed for Calculation" % (time.time() - startTime))
display(screen)
save_extension(screen, 'pic2')
