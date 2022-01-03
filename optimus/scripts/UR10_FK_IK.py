#!/usr/bin/env python

# Inverse Kinematics Validation
# Tracking a circle using Inverse Kinematics

# Importing modules
from math import sin, cos, pi
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(suppress=True)

# Initializing DH Paramters
# DH Parameter a
a1 = 0
a2 = -0.6127
a3 = -0.5715
a4 = 0
a5 = 0
a6 = 0

# DH Parameter alpha
alpha1 = pi/2
alpha2 = 0
alpha3 = 0
alpha4 = pi/2
alpha5 = -pi/2
alpha6 = 0

# DH Parameter d
d1 = 0.1807
d4 = 0.1741
d5 = 0.1198
d6 = 0.1165

# DH Parameter Theta
q1 = 0
q2 = 0
q3 = 0
q4 = 0
q5 = 0
q6 = 0

# Function to compute homogeneous transformation matrix using DH parameters
def generate_Ti(a, alpha, d, theta):
    
    T = np.array([[cos(theta), -sin(theta)*cos(alpha), sin(theta)*sin(alpha), a*cos(theta)],
                [sin(theta), cos(theta)*cos(alpha), -cos(theta)*sin(alpha), a*sin(theta)],
                [0, sin(alpha), cos(alpha), d],
                [0, 0, 0, 1]])
    
    return T

# Function to retrieve Z vectors from homogeneous transformation matrices
def get_Zi(T):
    return np.array(T[0:3, 2])

# Function to retrieve O vectors from homogeneous transformation matrices
def get_Oi(T):
    return np.array(T[0:3, 3])

# Function to generate Jacobian matrix columns 
def generate_Ji(Z, O, On):
  return np.concatenate([np.cross(Z, (On - O)), Z])


def main():
    # Defining charateristics for circle tracking
    radius = .100 # [mm], Radius of the circle
    circ_pts = 360 # Number of points taken on the circle
    time = 5 # [seconds], Time to draw the circle
    delta_t = time/circ_pts # Time to draw each consecutive arc
    arc_length = (2*pi)/circ_pts # Length of each arc
    theta_dot = 2*pi/time # Differential of theta with respect to time

    delta_theta = 0.0 # Initializing theta
    q_prev = np.array([[q1, q2, q3, q4, q5, q6]]).transpose() # Initializing q_prev

    x_dot_ = list() # List to store the x_dot values
    z_dot_ = list() # List to store the z_dot values

    circ_x = [0] # Circle x points
    circ_z = [.780] # Circle z points

    end_x = [0] # End-Effector x points
    end_z = [.780] # End-Effector z points

    for i in range(circ_pts):

        # Computing Homogeneous Transformation Matrices
        T1 = generate_Ti(a1, alpha1, d1, q_prev[0])
        T2 = generate_Ti(a2, alpha2, 0, q_prev[1])
        T3 = generate_Ti(a3, alpha3, 0, q_prev[2])
        T4 = generate_Ti(a4, alpha4, d4, q_prev[3])
        T5 = generate_Ti(a5, alpha5, d5, q_prev[4])
        T6 = generate_Ti(a6, alpha6, d6, q_prev[5])

        # Forward Kinematics
        T_0_1 = T1
        T_1_2 = np.matmul(T_0_1, T2)
        T_2_3 = np.matmul(T_1_2, T3)
        T_3_4 = np.matmul(T_2_3, T4)
        T_4_5 = np.matmul(T_3_4, T5)
        T_5_6 = np.matmul(T_4_5, T6)

        # Computing Z vectors from Transformation Matrices
        Z0 = np.array([0, 0, 1])
        Z1 = get_Zi(T_0_1)
        Z2 = get_Zi(T_1_2)
        Z3 = get_Zi(T_2_3)
        Z4 = get_Zi(T_3_4)
        Z5 = get_Zi(T_4_5)
        Z6 = get_Zi(T_5_6)

        # Computing O vectors from Transformation Matrices
        O0 = np.array([0, 0, 0])
        O1 = get_Oi(T_0_1)
        O2 = get_Oi(T_1_2)
        O3 = get_Oi(T_2_3)
        O4 = get_Oi(T_3_4)
        O5 = get_Oi(T_4_5)
        O6 = get_Oi(T_5_6)
        
        # Computing Ji
        J1 = generate_Ji(Z0, O0, O6)
        J2 = generate_Ji(Z1, O1, O6)
        J3 = generate_Ji(Z2, O2, O6)
        J4 = generate_Ji(Z3, O3, O6)
        J5 = generate_Ji(Z4, O4, O6)
        J6 = generate_Ji(Z5, O5, O6)

        J = np.array([J1, J2, J3, J4, J5, J6]).transpose()
        J_ = np.linalg.pinv(J) # Taking the pseudo-inverse of the Jacobian Matrix
        
        # Computing points on the circle and respect x_dot and z_dot values
        circ_x.append(radius * sin(delta_theta))
        x_dot = radius * theta_dot * cos(delta_theta)
        x_dot_.append(x_dot)
        
        circ_z.append(.780 - (radius - radius * cos(delta_theta)))
        z_dot = -radius * theta_dot * sin(delta_theta)
        z_dot_.append(z_dot)
        
        delta_theta += (2*pi)/circ_pts # Updating delta_theta
        
        # Inverse Kinematics
        eta = np.array([[x_dot, 0, z_dot, 0, 0, 0]]).transpose()
        q_curr_dot = np.matmul(J_, eta)
        q_curr = q_prev + q_curr_dot * delta_t
        q_prev = q_curr
        
        # Using end-effector velocities generated from IK to obtain end-effector position
        x = end_x[i] + x_dot_[i] * delta_t
        end_x.append(x)
        z = end_z[i] + z_dot_[i] * delta_t
        end_z.append(z)
        # print(x, z)

    # Setting up matplotlib plots
    fig, axs = plt.subplots(1, 3)
    axs[0].set_title("Circle to Draw")
    axs[0].plot(circ_x, circ_z)
    axs[1].set_title("Circle Drawn")
    axs[1].plot(end_x, end_z, 'orange')
    axs[2].set_title("Overlap")
    axs[2].plot(circ_x, circ_z)
    axs[2].plot(end_x, end_z, 'orange')
    axs[2].legend(['Circle to Draw', 'Circle Drawn'], loc=0)
    # manager = plt.get_current_fig_manager()
    # manager.full_screen_toggle()
    # plt.savefig('result.png')
    plt.show()

if __name__ == '__main__':
    main()