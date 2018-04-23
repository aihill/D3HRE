import numpy as np

def min_max_model(power, use, battery_capacity):
    """
    Minimal maximum battery model
    :param power: Pandas TimeSeries of total power from renewable system
    :param use: float unit W fixed load of the power system
    :param battery_capacity: float unit Wh battery capacity
    :return: list energy history in battery
    """
    power = power.tolist()
    energy = 0
    energy_history = []
    for p in power:
        energy = min(battery_capacity, max(0, energy + (p - use) * 1))
        energy_history.append(energy)

    return energy_history


def soc_model_fixed_load(power, use, battery_capacity, depth_of_discharge=1,
                         discharge_rate=0.005, battery_eff=0.9, discharge_eff=0.8):
    """
    Battery state of charge model with fixed load.

    :param power: Pandas TimeSeries of total power from renewable system
    :param use: float unit W fixed load of the power system
    :param battery_capacity: float unit Wh battery capacity
    :param depth_of_discharge: float 0 to 1 maximum allowed discharge depth
    :param discharge_rate: self discharge rate
    :param battery_eff: optional 0 to 1 battery energy store efficiency default 0.9
    :param discharge_eff: battery discharge efficiency 0 to 1 default 0.8
    :return: tuple SOC: state of charge, energy history: E in battery,
    unmet_history: unmet energy history, waste_history: waste energy history
    """
    DOD = depth_of_discharge
    power = power.tolist()
    use_history = []
    waste_history = []
    unmet_history = []
    energy_history = []
    energy = 0
    for p in power:
        if p >= use:
            use_history.append(use)
            unmet_history.append(0)
            energy_new = energy * (1 - discharge_rate) + (p - use) * battery_eff
            if energy_new < battery_capacity:
                energy = energy_new  # battery energy got update
                waste_history.append(0)
            else:
                waste_history.append(p - use)
                energy = energy

        elif p < use:
            energy_new = energy * (1 - discharge_rate) + (p - use) / discharge_eff
            if energy_new > (1 - DOD) * battery_capacity:
                energy = energy_new
                unmet_history.append(0)
                waste_history.append(0)
                use_history.append(use)
            elif energy * (1 - discharge_rate) + p * battery_eff < battery_capacity:
                energy = energy * (1 - discharge_rate) + p * battery_eff
                unmet_history.append(use - p)
                use_history.append(0)
                waste_history.append(0)
            else:
                unmet_history.append(use - p)
                use_history.append(0)
                waste_history.append(p)
                energy = energy

        energy_history.append(energy)

    if battery_capacity == 0:
        SOC = np.array(energy_history)
    else:
        SOC = np.array(energy_history) / battery_capacity
    return SOC, energy_history, unmet_history, waste_history, use_history


class Battery():

    def __init__(self, capacity, depth_of_discharge=1,
                         discharge_rate=0.005, battery_eff=0.9, discharge_eff=0.8):
        self.capacity = capacity

        self.depth_of_discharge = depth_of_discharge
        self.discharge_rate = discharge_rate
        self.battery_eff = battery_eff
        self.discharge_eff = discharge_eff

    def run(self, power, use):

        DOD = self.depth_of_discharge
        battery_capacity = self.capacity
        discharge_rate = self.discharge_rate
        discharge_eff = self.discharge_eff
        battery_eff = self.battery_eff


        use_history = []
        waste_history = []
        unmet_history = []
        energy_history = []
        energy = 0
        for p, u in zip(power, use):
            if p >= u:
                use_history.append(u)
                unmet_history.append(0)
                energy_new = energy * (1 - discharge_rate) + (p - u) * battery_eff
                if energy_new < battery_capacity:
                    energy = energy_new  # battery energy got update
                    waste_history.append(0)
                else:
                    waste_history.append(p - u)
                    energy = energy

            elif p < u:
                energy_new = energy * (1 - discharge_rate) + (p - u) / discharge_eff
                if energy_new > (1 - DOD) * battery_capacity:
                    energy = energy_new
                    unmet_history.append(0)
                    waste_history.append(0)
                    use_history.append(u)
                elif energy * (1 - discharge_rate) + p * battery_eff < battery_capacity:
                    energy = energy * (1 - discharge_rate) + p * battery_eff
                    unmet_history.append(u - p)
                    use_history.append(0)
                    waste_history.append(0)
                else:
                    unmet_history.append(u - p)
                    use_history.append(0)
                    waste_history.append(p)
                    energy = energy

            energy_history.append(energy)

            if battery_capacity == 0:
                SOC = np.array(energy_history)
            else:
                SOC = np.array(energy_history) / battery_capacity

            self.SOC = SOC
            self.energy_history = energy_history
            self.unmet_history = unmet_history
            self.waste_history = waste_history
            self.use_history = use_history

    def lost_power_supply_probability(self):
        LPSP = 1 - self.unmet_history.count(0) / len(self.energy_history)
        return LPSP

class Soc_model_variable_load():

    def __init__(self, battery, power, load):
        self.battery = battery
        self.battery.run(power, load)

    def get_lost_power_supply_probability(self):

        return self.battery.lost_power_supply_probability()

    def get_information_quality_performance_index(self):

        pass



def soc_model_variable_load(power, use, battery_capacity, depth_of_discharge=1,
                         discharge_rate=0.005, battery_eff=0.9, discharge_eff=0.8):
    """
    Battery state of charge model with fixed load.

    :param power: Pandas TimeSeries of total power from renewable system
    :param use: float unit W fixed load of the power system
    :param battery_capacity: float unit Wh battery capacity
    :param depth_of_discharge: float 0 to 1 maximum allowed discharge depth
    :param discharge_rate: self discharge rate
    :param battery_eff: optional 0 to 1 battery energy store efficiency default 0.9
    :param discharge_eff: battery discharge efficiency 0 to 1 default 0.8
    :return: tuple SOC: state of charge, energy history: E in battery,
    unmet_history: unmet energy history, waste_history: waste energy history
    """
    DOD = depth_of_discharge
    power = power.tolist()
    use = use.tolist()
    use_history = []
    waste_history = []
    unmet_history = []
    energy_history = []
    energy = 0
    for p, u in zip(power, use):
        if p >= u:
            use_history.append(u)
            unmet_history.append(0)
            energy_new = energy * (1 - discharge_rate) + (p - u) * battery_eff
            if energy_new < battery_capacity:
                energy = energy_new  # battery energy got update
                waste_history.append(0)
            else:
                waste_history.append(p - u)
                energy = energy

        elif p < u:
            energy_new = energy * (1 - discharge_rate) + (p - u) / discharge_eff
            if energy_new > (1 - DOD) * battery_capacity:
                energy = energy_new
                unmet_history.append(0)
                waste_history.append(0)
                use_history.append(use)
            elif energy * (1 - discharge_rate) + p * battery_eff < battery_capacity:
                energy = energy * (1 - discharge_rate) + p * battery_eff
                unmet_history.append(u - p)
                use_history.append(0)
                waste_history.append(0)
            else:
                unmet_history.append(u - p)
                use_history.append(0)
                waste_history.append(p)
                energy = energy

        energy_history.append(energy)

    if battery_capacity == 0:
        SOC = np.array(energy_history)
    else:
        SOC = np.array(energy_history) / battery_capacity
    return SOC, energy_history, unmet_history, waste_history, use_history

if __name__ == '__main__':
    b1 = Battery(10)
    b1.run([1,1,1], [1,1,1])
    b1.run( [1, 1, 1], [10, 10, 10])
    print(b1.lost_power_supply_probability())