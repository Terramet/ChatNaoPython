import requests
import json
import rclpy
from geometry_msgs.msg import Twist

func_desc = {
    "name": "moveRobot",
    "description": "Control the TurtleBot4 robot's movement",
    "parameters": {
        "type": "object",
        "properties": {
            "linear": {
                "type": "number",
                "description": "Linear velocity"
            },
            "angular": {
                "type": "number",
                "description": "Angular velocity"
            }
        },
        "required": ["linear", "angular"]
    }
}

def command_moveRobot(arguments):
    args = json.loads(arguments)
    linear_vel = args["linear"]
    angular_vel = args["angular"]

    rclpy.init()
    node = rclpy.create_node("turtlebot_control_node")
    cmd_pub = node.create_publisher(Twist, "cmd_vel", 10)
    
    twist = Twist()
    twist.linear.x = linear_vel
    twist.angular.z = angular_vel

    cmd_pub.publish(twist)
    
    node.destroy_node()
    rclpy.shutdown()

    result = {
        "status": "success",
        "message": "Robot movement command sent"
    }

    return json.dumps(result)

def register(function_manager):
    function_manager.register_command("moveRobot", command_moveRobot)
    function_manager.register_function_with_gpt(func_desc)
