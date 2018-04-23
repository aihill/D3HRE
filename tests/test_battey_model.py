from D3HRE.core.mission_utility import Mission
from D3HRE.core.battery_models import Soc_model_variable_load, Battery

from PyResis import propulsion_power

import numpy as np

test_route =  np.array([[  10.69358 ,  -178.94713892], [  11.06430687, +176.90022735]])


test_ship = propulsion_power.Ship()
test_ship.dimension(5.72, 0.248, 0.76, 1.2, 5.72/(0.549)**(1/3),0.613)

power_consumption_list = {'single_board_computer': {'power': [2, 10], 'duty_cycle': 0.5},
                              'webcam': {'power': [0.6], 'duty_cycle': 1},
                              'gps': {'power': [0.04, 0.4], 'duty_cycle': 0.9},
                              'imu': {'power': [0.67, 1.1], 'duty_cycle': 0.9},
                              'sonar': {'power': [0.5, 50, 0.2], 'duty_cycle': 0.5},
                              'ph_sensor': {'power': [0.08, 0.1], 'duty_cycle': 0.95},
                              'temp_sensor': {'power': [0.04], 'duty_cycle': 1},
                              'wind_sensor': {'power': [0.67, 1.1], 'duty_cycle': 0.5},
                              'servo_motors': {'power': [0.4, 1.35], 'duty_cycle': 0.5},
                              'radio_transmitter': {'power': [0.5, 20], 'duty_cycle': 0.2}}

b1 = Battery(10)
model = Soc_model_variable_load(b1, [1,2,3],[1,2,3])
model2 = Soc_model_variable_load(Battery(10), [1,1,1], [10, 10, 10])


def test_lpsp_calc():
    assert model.get_lost_power_supply_probability() == 0
    assert model2.get_lost_power_supply_probability() == 1





