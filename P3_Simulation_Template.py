ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3A' # Enter the project identifier i.e. P2A or P2B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.1 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.2
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.30
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.30
bin4_color = [0,0,0]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3B':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

'''Due to unforseen circumstances early on in development, most of the
functions were written by one team member. That being said, each function was
tweaked and fixed by both members of the computing team with improvements being
added as a group effort.'''



attributes= [] #Keeps track of all bottles in use
loaded = [] #Keeps track of what is loaded onto q-bot
q_bot_mass=0
def start():
    token=int(input("Hi there, I'm Edward the trash sorted. How many rounds of trash sorting do I have to do today?"))
    dropp_off=list()
    dropp_off_dist=0
    #Spawn a bottle. I need this seperate from the other prep pick ups
    #due to technical reasons
    attributes.append(table.dispense_container(random.randrange(1,6),True))
    index=0
    while index<token: #Repeat trash seperating cycle as needed
        load_container(attributes[0])
        current_drop=attributes[0][2]
        if current_drop=="Bin01":
                dropp_off=[1,0,0]
                dropp_off_dist=0.1
        elif current_drop=="Bin02":
                dropp_off=[0,1,0]
                dropp_off_dist=0.2
        elif current_drop=="Bin03":
                dropp_off=[0,0,1]
                dropp_off_dist=0.3
        else:
                dropp_off=[1,1,1]
                dropp_off_dist=0.3
        
        attributes.pop(0)
        prep_pick_up(current_drop,dropp_off_dist,dropp_off)
        index+=1
    
#By Johnn    
def prep_pick_up(current_drop,dropp_off_dist,dropp_off):
    #Spawn bottle and decide what to do
    homex,homey,homez=bot.position()
    global q_bot_mass
    while True:
        new_container = table.dispense_container(random.randrange(1,6),True)
        attributes.append(new_container)
        #Decide if we should load or send
        if new_container[2]== current_drop and new_container[1]+q_bot_mass<90 and len(loaded)<3:
            load_container(new_container)
            
            attributes.pop(0)
        else:
            follow_track(dropp_off_dist,dropp_off)
            
            dump()
            go_home(homex,homey,homez)
            bot.deactivate_color_sensor()
            bot.deactivate_ultrasonic_sensor()
            break
#By Andrew
def load_container(new_container):#Put bottle on q-bot
    global q_bot_mass
    loaded_position = [[0.02, -0.58, 0.591],[0.02, -0.51, 0.581],[0.02, -0.44, 0.581]] #Positions of bottles on q-bot
    time.sleep(0.5)
    arm.move_arm(0.651, 0, 0.255) #Move arm to pick up zone and grab
    time.sleep(0.5)
    arm.control_gripper(38)
    time.sleep(1)

    arm.move_arm(0.406,0.0,0.483) #Move back to home then to drop off
    time.sleep(0.5)
    arm.move_arm(0.01, -0.239, 0.661)
    time.sleep(1)
    arm.move_arm(loaded_position[len(loaded)][0],loaded_position[len(loaded)][1],loaded_position[len(loaded)][2]-0.1)
    time.sleep(1)
    arm.control_gripper(-38)
    time.sleep(1)

    
    arm.rotate_shoulder(-20) #Return home
    arm.move_arm(0.406,0.0,0.483)
    loaded.append(new_container)
    q_bot_mass+=new_container[1]
    time.sleep(1)

#By John
def follow_track(dist, colour):#follow track
    bot.activate_line_following_sensor()
    bot.activate_color_sensor()
    bot.activate_ultrasonic_sensor()
    turn_direction=0
    while True: #This is a turning function
        if bot.line_following_sensors()==[1,1]:
            bot.set_wheel_speed([0.05,0.05])
        #elif  bot.line_following_sensors()==[0,1]:
            #bot.set_wheel_speed([0.05,0.025])
        #elif  bot.line_following_sensors()==[1,0]:
            #bot.set_wheel_speed([0.025,0.05])
        elif  bot.line_following_sensors()==[0,0]:
            print( "IDK what to do man")
            bot.set_wheel_speed([2,2])

        #When the parameters of the drop off bin have been detected we dump
        if bot.read_color_sensor()[0]==colour and bot.read_ultrasonic_sensor()<dist-0.05:
            time.sleep(2)
            bot.stop()
            
            return
#By Andrew
def adjust(): #Turn bot back and forth to find line again
    start=time.time()
    while bot.line_following_sensors()!=[1,1]:
        bot.set_wheel_speed([0.02,-0.02])
        if time.time()-start>5:
            break
    start=time.time()
    while bot.line_following_sensors()!=[1,1]:
        bot.set_wheel_speed([-0.02,0.02])
        if time.time()-start>10:
            break
    time.sleep(0.3)
        
#Function written by Andrew
def dump(): #Drive to bin and dump.
    global q_bot_mass
    if len(loaded)>0:
        bot.rotate(90) #Turns to bin
        start=time.time()
        while bot.read_ultrasonic_sensor()>0.1: #Drive until close
            bot.forward_distance(0.05)
        duration=time.time()-start#Record time needed to travel
        bot.rotate(-100)
        time.sleep(1)
        bot.activate_linear_actuator()#Dump
        #Multistep dumping was an idea from John
        bot.rotate_hopper(15) #Adjust this to adjust power
        time.sleep(0.5)
        bot.rotate_hopper(30) #Adjust this to adjust power
        time.sleep(0.5)
        bot.rotate_hopper(60) #Adjust this to adjust power
        time.sleep(0.5)
        bot.rotate_hopper(75) #Adjust this to adjust power
        time.sleep(0.5)
        bot.rotate_hopper(90) #Adjust this to adjust power
        time.sleep(2)
        bot.deactivate_linear_actuator()
        loaded.clear()
        q_bot_mass=0 #Return to on track position
        bot.rotate(-80)
        bot.forward_time(duration*0.5)
        bot.rotate(85) #offset
        


#By John
def go_home(homex,homey,homez):
    #Bot finds it's home position and drives until it hits a line about that area
    x,y,z=bot.position()
    while (x>homex+0.1 or x<homex-0.1) or (y>homey+0.01 or y<homey-0.01):
        x,y,z=bot.position()
        if bot.line_following_sensors()==[1,1]:
            bot.set_wheel_speed([0.05,0.05])
        elif  bot.line_following_sensors()==[0,1]:
            bot.set_wheel_speed([0.05,0.025])
        elif  bot.line_following_sensors()==[1,0]:
            bot.set_wheel_speed([0.025,0.05])
        elif  bot.line_following_sensors()==[0,0]:
            print( "IDK what to do man")
            bot.stop()
            adjust()
            
    bot.stop()
    bot.deactivate_line_following_sensor()
    bot.position()
    time.sleep(1)
    
    bot.stop()
#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    
