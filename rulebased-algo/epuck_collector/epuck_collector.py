"""epuck_collector controller."""

# You may need to import some classes of the controller module. Ex:
from controller import Robot, Receiver, Motor
import logging as log
import msgpack
from rulebasedAlgo import  CollectorLogik
# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

motorLeft:Motor = robot.getDevice('left wheel motor')
motorRight:Motor = robot.getDevice('right wheel motor')
motorLeft.setPosition(float('inf')) #this sets the motor to velocity control instead of position control
motorRight.setPosition(float('inf'))
motorLeft.setVelocity(0)
motorRight.setVelocity(0)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getMotor('motorname')
#  ds = robot.getDistanceSensor('dsname')
#  ds.enable(timestep)

rec:Receiver = robot.getDevice("receiver")
rec.enable(timestep)
camera = robot.getDevice("camera")
camera.enable(timestep)
maxVelocity = motorLeft.getMaxVelocity()
log.basicConfig(level=log.INFO, format='%(asctime)s %(filename)s %(levelname)s: %(message)s')

# Main loop:
# - perform simulation steps until Webots is stopping the controller

"""
WICHTIG:
    Bei dem erstellen des Codes ist aufgefallen, dass
    bei dem Reset der Umgebung bereits vor dem Start dieser
    einige Bälle gespawnt werden.
    Diese können NICHT vom Roboter eingesammelt werden und
    werden demnach dazu führen, dass der Roboter diese fixiert
    und ggf. nicht weiter sammelt.

WORKAROUND:
    Umgangen werden kann dies durch das manuelle löschen
    der durch diesen Bug entstehenden Kugeln in der
    Webbots-Umgebung.
"""
 
cl = CollectorLogik()
      
while robot.step(timestep) != -1:
    # Process sensor data here.
    image = camera.getImageArray()

    v_left, v_right = cl.choose(image)
    motorRight.setVelocity(v_right)
    motorLeft.setVelocity(v_left)
        
    while rec.getQueueLength() > 0:
        msg_dat = rec.getData()
        rec.nextPacket()
        msg = msgpack.unpackb(msg_dat)
        log.info(msg)
