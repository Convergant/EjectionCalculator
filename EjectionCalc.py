import math, mysql.connector

G = 6.67408 * (10 ** (-11))


class Orbit:
    def __init__(self, apoapsis, periapsis, host, inclination=0.0):
        self.__apoapsis = apoapsis
        self.__periapsis = periapsis
        self.__SMA = (apoapsis + periapsis) / 2
        self.__inclination = inclination
        self.__host = host
        self.__period = self.__calculate_period()
        self.__eccentricity = self.__calculate_eccentricity()

    def __calculate_period(self):
        try:
            return 2 * math.pi * math.sqrt((self.__SMA ** 3) / self.__host.get_mu())

        except AttributeError:
            return 0

    def __calculate_eccentricity(self):
        try:
            return (self.__apoapsis - self.__periapsis) / (self.__apoapsis + self.__periapsis)

        except ZeroDivisionError:
            return 0

    def get_apoapsis(self):
        return self.__apoapsis

    def set_apoapsis(self, apoapsis):
        assert apoapsis >= self.__periapsis
        self.__apoapsis = apoapsis
        self.__SMA = (self.__apoapsis + self.__periapsis) / 2
        self.__period = self.__calculate_period()
        self.__eccentricity = self.__calculate_eccentricity()

    def get_periapsis(self):
        return self.__periapsis

    def set_periapsis(self, periapsis):
        assert periapsis <= self.__apoapsis
        self.__periapsis = periapsis
        self.__SMA = (self.__apoapsis + self.__periapsis) / 2
        self.__period = self.__calculate_period()
        self.__eccentricity = self.__calculate_eccentricity()

    def get_SMA(self):
        return self.__SMA

    def get_eccentricity(self):
        return self.__eccentricity

    def get_inclination(self):
        return self.__inclination

    def set_inclination(self, inclination):
        self.__inclination = inclination

    def get_period(self):
        return self.__period

    def get_host(self):
        return self.__host

    def velocity(self, radius):
        assert self.__periapsis <= radius <= self.__apoapsis
        return math.sqrt(self.__host.get_mu() * (2 / radius - 1 / self.__SMA))


class Body(Orbit):
    def __init__(self, mass, radius, apoapsis, periapsis, host, inclination=0.0, name="", colour="", alt=0):
        super().__init__(apoapsis, periapsis, host, inclination)
        self.__mass = mass
        self.__mu = G * mass
        self.__radius = radius
        self.__r_SOI = self.__calculate_SOI()
        self.__name = name
        self.__colour = colour
        self.__alt = alt

    def __calculate_SOI(self):
        try:
            return self.get_SMA() * (self.__mass / self.get_host().get_mass()) ** (2 / 5)

        except AttributeError:
            return float("inf")

    def get_mass(self):
        return self.__mass

    def set_mass(self, mass):
        self.__mass = mass
        self.__mu = G * mass

    def get_mu(self):
        return self.__mu

    def get_radius(self):
        return self.__radius

    def set_radius(self, radius):
        self.__radius = radius

    def get_r_SOI(self):
        return self.__r_SOI

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_colour(self):
        return self.__colour

    def set_colour(self, colour):
        self.__colour = colour

    def get_altitude(self):
        return self.__alt

    def set_altitude(self, altitude):
        self.__alt = altitude


class Transfer:
    def __init__(self, origin, destination, parking_orbit, target_orbit):
        assert parking_orbit.get_host() == origin
        assert target_orbit.get_host() == destination
        assert origin.get_host().get_name() == destination.get_host().get_name()

        self.__origin = origin
        self.__destination = destination
        self.__parking_orbit = parking_orbit
        self.__target_orbit = target_orbit

        res = self.__calculate()

        self.__phase_angle = res[0]
        self.__ejection_angle = res[1]
        self.__ejection_dv = res[2]
        self.__capture_dv = res[3]
        self.__transfer_time = res[4]

    def __calculate(self):
        origin_SMA = self.__origin.get_SMA()
        destination_SMA = self.__destination.get_SMA()

        transfer_orbit = Orbit(greater(origin_SMA, destination_SMA), lesser(origin_SMA, destination_SMA), self.__origin.get_host())

        v_transfer_origin = transfer_orbit.velocity(origin_SMA)
        v_transfer_destination = transfer_orbit.velocity(destination_SMA)

        v_soi_origin = abs(self.__origin.velocity(origin_SMA) - v_transfer_origin)
        v_soi_destination = abs(self.__destination.velocity(destination_SMA) - v_transfer_destination)

        v_orbit_origin = self.__parking_orbit.velocity(self.__parking_orbit.get_SMA())
        v_orbit_target = self.__target_orbit.velocity(self.__target_orbit.get_SMA())

        v_pe_origin = math.sqrt(v_soi_origin ** 2 + 2 * self.__origin.get_mu() * (1 / self.__parking_orbit.get_SMA() - 1 / self.__origin.get_r_SOI()))
        v_pe_destination = math.sqrt(v_soi_destination ** 2 + 2 * self.__destination.get_mu() * (1 / self.__target_orbit.get_SMA() - 1 / self.__destination.get_r_SOI()))

        deltav_transfer = abs(v_pe_origin - v_orbit_origin)
        deltav_capture = abs(v_pe_destination - v_orbit_target)

        transfer_time = transfer_orbit.get_period() / 2

        phase_angle = math.pi * (1 - 1/math.sqrt(8) * math.sqrt((self.__origin.get_SMA() / self.__destination.get_SMA() + 1) ** 3))

        while abs(phase_angle) > 2 * math.pi:
            phase_angle += 2 * math.pi * ((phase_angle < 0) - (phase_angle > 0))

        if phase_angle < -math.pi:
            phase_angle = 2 * math.pi + phase_angle

        a_esc = -self.__origin.get_mu() / (v_soi_origin ** 2)

        b_esc = math.sqrt(self.__parking_orbit.get_SMA() ** 2 - 2 * a_esc * self.__parking_orbit.get_SMA())

        e_esc = math.sqrt(1 + b_esc ** 2 / a_esc ** 2)

        ejection_angle = math.pi - math.acos(1 / e_esc)

        return [phase_angle, ejection_angle, deltav_transfer, deltav_capture, transfer_time]

    def get_origin(self):
        return self.__origin

    def get_destination(self):
        return self.__destination

    def get_parking_orbit(self):
        return self.__parking_orbit

    def get_target_orbit(self):
        return self.__target_orbit

    def get_phase_angle(self):
        return self.__phase_angle

    def get_ejection_angle(self):
        return self.__ejection_angle

    def get_ejection_deltav(self):
        return self.__ejection_dv

    def get_capture_deltav(self):
        return self.__capture_dv

    def get_transfer_time(self):
        return self.__transfer_time

    def __str__(self):
        msg = "Phase Angle: " + str(round(math.degrees(self.__phase_angle), 2)) + "°\n"
        msg += "Ejection Angle: " + str(round(math.degrees(self.__ejection_angle), 2)) + "°\n"
        msg += "Ejection Δv: " + str(int(round(self.__ejection_dv))) + " m/s\n"
        msg += "Capture Δv: " + str(int(round(self.__capture_dv))) + " m/s\n"
        msg += "Transfer Time: " + str(int(round(self.__transfer_time))) + "s"

        return msg


def get_names():
    sql = "SELECT name FROM BODIES WHERE host != ''"
    cursor.execute(sql)
    names = cursor.fetchall()
    names = [c[0] for c in names]

    return names


def read_body(body_name, give_body=True):
    if body_name in names:
        sql = "SELECT * FROM bodies WHERE name = "
        cursor.execute(sql + "'" + body_name + "'")
        this_body = cursor.fetchall()[0]
        cursor.execute(sql + "'" + this_body[5] + "'")
        host = cursor.fetchall()[0]

        if give_body:
            return init_body(this_body, host)

        else:
            return this_body


def init_body(body_list, host_list):
    host = Body(float(host_list[1]), float(host_list[2]), 0, 0, name=host_list[0], host=None)
    return Body(float(body_list[1]), float(body_list[2]), float(body_list[3]), float(body_list[4]),
                host=host, inclination=float(body_list[6]), name=body_list[0], colour=body_list[7],
                alt=int(body_list[8]))


def greater(x, y):
    return x * (x > y) + y * (y > x)


def lesser(x, y):
    return x * (y > x) + y * (x > y)


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="bodies"
)
cursor = mydb.cursor()
names = get_names()

if __name__ == "__main__":
    Earth = read_body("planets.csv", "Earth")
    Mars = read_body("planets.csv", "Mars")
    parking_orbit = Orbit(Earth.get_radius() + 300000, Earth.get_radius() + 300000, host=Earth)
    final_orbit = Orbit(Mars.get_radius() + 200000, Mars.get_radius() + 200000, host=Mars)
    transfer = Transfer(Earth, Mars, parking_orbit, final_orbit)
    print(transfer)


