#include <micro_ros_arduino.h>

#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <geometry_msgs/msg/vector3.h>

#define MAX_RPM 5000
#define LED_PIN 13

int pwmL_pin[4] = {1,4,13,22};
int pwmR_pin[4] = {0,5,12,23};

rcl_subscription_t subscriber;
geometry_msgs__msg__Vector3 msg;

rclc_executor_t executor;
rcl_allocator_t allocator;
rclc_support_t support;
rcl_node_t node;

IntervalTimer motorTimer;

float vx = 0;
float vy = 0;
float omega = 0;

#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// -------- Error Loop --------

void error_loop(){
  while(1){
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(100);
  }
}


// ---------------- Inverse Kinematics ----------------

void inverseKinematics(float vx, float vy, float omega, float* rpms)
{
    rpms[0] = map(-vx + vy + omega/2, -255,255,-MAX_RPM,MAX_RPM);
    rpms[1] = map( vx + vy + omega/2, -255,255,-MAX_RPM,MAX_RPM);
    rpms[2] = map(-vx - vy + omega/2, -255,255,-MAX_RPM,MAX_RPM);
    rpms[3] = map( vx - vy + omega/2, -255,255,-MAX_RPM,MAX_RPM);
}


// ---------------- Motor Driver ----------------

void runMotor(int pwm_val, int pwmLPin, int pwmRPin)
{
    analogWrite(pwmRPin,(pwm_val <=0 ? -pwm_val : 0));
    analogWrite(pwmLPin,(pwm_val >=0 ? pwm_val : 0));
}

void motor_update()
{
    float rpm_cmd[4];

    inverseKinematics(vx,vy,omega,rpm_cmd);

    for(int i=0;i<4;i++)
    {
        rpm_cmd[i] = constrain(rpm_cmd[i],-MAX_RPM,MAX_RPM);
        runMotor((int)rpm_cmd[i],pwmL_pin[i],pwmR_pin[i]);
    }
}


// ---------------- ROS Callback ----------------

void subscription_callback(const void * msgin)
{
    const geometry_msgs__msg__Vector3 * incoming =
        (const geometry_msgs__msg__Vector3 *)msgin;

    // Read values from ROS2 topic
    float x_error = incoming->x;
    float area_error = incoming->y;
    float z_val = incoming->z;

    // Print received values
    Serial.print("Received -> ");
    Serial.print("x: ");
    Serial.print(x_error);
    Serial.print("  y: ");
    Serial.print(area_error);
    Serial.print("  z: ");
    Serial.println(z_val);

    // Control logic
    vy = constrain(x_error * 0.05, -255, 255);
    vx = constrain(area_error * 0.0005, -255, 255);
    omega = 0;
}


// ---------------- Setup ----------------

void setup()
{
    set_microros_transports();

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    Serial.begin(115200);
    delay(2000);

    analogWriteResolution(14);

    allocator = rcl_get_default_allocator();

    // SAME INIT SEQUENCE AS WORKING INT32 CODE
    RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

    RCCHECK(rclc_node_init_default(
        &node,
        "teensy_align",
        "",
        &support));

    RCCHECK(rclc_subscription_init_default(
        &subscriber,
        &node,
        ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Vector3),
        "alignment_error"));

    RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));

    RCCHECK(rclc_executor_add_subscription(
        &executor,
        &subscriber,
        &msg,
        &subscription_callback,
        ON_NEW_DATA));

    motorTimer.begin(motor_update,5000);
}


// ---------------- Loop ----------------

void loop()
{
    //delay(100);

    RCSOFTCHECK(
        rclc_executor_spin_some(
            &executor,
            RCL_MS_TO_NS(5)
        )
    );
}