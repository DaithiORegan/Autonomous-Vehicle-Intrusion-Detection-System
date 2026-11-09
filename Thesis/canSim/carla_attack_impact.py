import carla
import csv
import math
import time
from pathlib import Path



HOST = "localhost"
PORT = 2000

NORMAL_DURATION = 10
ATTACK_DURATION = 4
POST_ATTACK_DURATION = 5

SAMPLE_INTERVAL = 0.05

ATTACK_STEER = 0.75

OUTPUT_FILE = Path(
    "canSim/logs/carla_attack_impact.csv"
)



print("=" * 70)
print("CARLA STEERING SPOOF SAFETY IMPACT TEST")
print("=" * 70)

client = carla.Client(
    HOST,
    PORT
)

client.set_timeout(10.0)

world = client.get_world()

print(
    "Connected:",
    world.get_map().name
)




settings = world.get_settings()
settings.no_rendering_mode = False
world.apply_settings(settings)



blueprints = world.get_blueprint_library()

teslas = blueprints.filter(
    "vehicle.tesla.model3"
)

if not teslas:
    raise RuntimeError(
        "Tesla Model 3 blueprint not found."
    )

vehicle_bp = teslas[0]

spawn_points = (
    world.get_map()
    .get_spawn_points()
)

vehicle = None

for spawn in spawn_points:

    vehicle = world.try_spawn_actor(
        vehicle_bp,
        spawn
    )

    if vehicle is not None:
        break


if vehicle is None:
    raise RuntimeError(
        "Could not spawn vehicle."
    )


print(
    "Vehicle spawned:",
    vehicle.type_id
)




vehicle.set_autopilot(True)

print(
    "Autopilot enabled."
)



spectator = world.get_spectator()


def update_camera():

    transform = vehicle.get_transform()
    forward = transform.get_forward_vector()

    camera_location = carla.Location(
        x=(
            transform.location.x
            - forward.x * 7.0
        ),
        y=(
            transform.location.y
            - forward.y * 7.0
        ),
        z=(
            transform.location.z
            + 3.5
        )
    )

    camera_rotation = carla.Rotation(
        pitch=-12.0,
        yaw=transform.rotation.yaw,
        roll=0.0
    )

    spectator.set_transform(
        carla.Transform(
            camera_location,
            camera_rotation
        )
    )


def get_speed_kmh():

    velocity = vehicle.get_velocity()

    speed_mps = math.sqrt(
        velocity.x ** 2
        + velocity.y ** 2
        + velocity.z ** 2
    )

    return speed_mps * 3.6




def distance_2d(
    x1,
    y1,
    x2,
    y2
):

    return math.sqrt(
        (x2 - x1) ** 2
        +
        (y2 - y1) ** 2
    )




def yaw_difference(
    yaw1,
    yaw2
):

    difference = (
        yaw2 - yaw1
    )

    # Normalise to -180 to +180 degrees
    difference = (
        difference + 180
    ) % 360 - 180

    return difference




OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

file = open(
    OUTPUT_FILE,
    "w",
    newline=""
)

writer = csv.writer(file)

writer.writerow([
    "timestamp",
    "phase",
    "x",
    "y",
    "yaw",
    "speed_kmh",
    "steering",
    "brake",
    "throttle",
    "attack_active"
])




attack_start_state = None
attack_end_state = None




def log_state(
    phase,
    attack_active
):

    transform = vehicle.get_transform()
    control = vehicle.get_control()

    x = transform.location.x
    y = transform.location.y
    yaw = transform.rotation.yaw

    speed = get_speed_kmh()

    writer.writerow([
        time.time(),
        phase,
        x,
        y,
        yaw,
        speed,
        control.steer,
        control.brake,
        control.throttle,
        attack_active
    ])

    return {
        "x": x,
        "y": y,
        "yaw": yaw,
        "speed": speed,
        "steer": control.steer
    }




try:



    print()
    print("=" * 70)
    print("PHASE 1 - NORMAL AUTONOMOUS DRIVING")
    print("=" * 70)

    start = time.time()

    while (
        time.time() - start
        < NORMAL_DURATION
    ):

        update_camera()

        state = log_state(
            "normal",
            0
        )

        print(
            f"NORMAL | "
            f"Speed {state['speed']:6.2f} km/h | "
            f"Yaw {state['yaw']:7.2f} | "
            f"X {state['x']:7.2f} | "
            f"Y {state['y']:7.2f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )



    attack_start_transform = (
        vehicle.get_transform()
    )

    attack_start_state = {
        "x":
            attack_start_transform.location.x,

        "y":
            attack_start_transform.location.y,

        "yaw":
            attack_start_transform.rotation.yaw,

        "speed":
            get_speed_kmh()
    }



    print()
    print("!" * 70)
    print("STEERING SPOOF ATTACK ACTIVE")
    print("!" * 70)

    vehicle.set_autopilot(
        False
    )

    attack_start_time = time.time()

    while (
        time.time() - attack_start_time
        < ATTACK_DURATION
    ):

        update_camera()

        current_control = (
            vehicle.get_control()
        )

        malicious_control = (
            carla.VehicleControl(
                throttle=max(
                    current_control.throttle,
                    0.35
                ),
                steer=ATTACK_STEER,
                brake=0.0
            )
        )

        vehicle.apply_control(
            malicious_control
        )

        state = log_state(
            "attack",
            1
        )

        print(
            f"ATTACK | "
            f"Speed {state['speed']:6.2f} km/h | "
            f"Yaw {state['yaw']:7.2f} | "
            f"X {state['x']:7.2f} | "
            f"Y {state['y']:7.2f} | "
            f"Steer {ATTACK_STEER:4.2f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )




    attack_end_transform = (
        vehicle.get_transform()
    )

    attack_end_state = {
        "x":
            attack_end_transform.location.x,

        "y":
            attack_end_transform.location.y,

        "yaw":
            attack_end_transform.rotation.yaw,

        "speed":
            get_speed_kmh()
    }



    print()
    print("=" * 70)
    print("ATTACK ENDED - RESTORING AUTOPILOT")
    print("=" * 70)

    vehicle.set_autopilot(
        True
    )

    recovery_start = time.time()

    while (
        time.time() - recovery_start
        < POST_ATTACK_DURATION
    ):

        update_camera()

        state = log_state(
            "recovery",
            0
        )

        print(
            f"RECOVERY | "
            f"Speed {state['speed']:6.2f} km/h | "
            f"Yaw {state['yaw']:7.2f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )


finally:

    file.close()

    if vehicle is not None:

        vehicle.destroy()



if (
    attack_start_state is not None
    and attack_end_state is not None
):

    displacement = distance_2d(
        attack_start_state["x"],
        attack_start_state["y"],
        attack_end_state["x"],
        attack_end_state["y"]
    )

    heading_change = yaw_difference(
        attack_start_state["yaw"],
        attack_end_state["yaw"]
    )

    speed_change = (
        attack_end_state["speed"]
        -
        attack_start_state["speed"]
    )


    print()
    print("=" * 70)
    print("CYBER-PHYSICAL ATTACK IMPACT")
    print("=" * 70)

    print(
        f"Attack steering command: "
        f"{ATTACK_STEER:.2f}"
    )

    print()
    print("Before attack:")

    print(
        f"  Position X: "
        f"{attack_start_state['x']:.2f} m"
    )

    print(
        f"  Position Y: "
        f"{attack_start_state['y']:.2f} m"
    )

    print(
        f"  Heading: "
        f"{attack_start_state['yaw']:.2f} degrees"
    )

    print(
        f"  Speed: "
        f"{attack_start_state['speed']:.2f} km/h"
    )


    print()
    print("After attack:")

    print(
        f"  Position X: "
        f"{attack_end_state['x']:.2f} m"
    )

    print(
        f"  Position Y: "
        f"{attack_end_state['y']:.2f} m"
    )

    print(
        f"  Heading: "
        f"{attack_end_state['yaw']:.2f} degrees"
    )

    print(
        f"  Speed: "
        f"{attack_end_state['speed']:.2f} km/h"
    )


    print()
    print("Measured attack effect:")

    print(
        f"  2D displacement during attack: "
        f"{displacement:.2f} m"
    )

    print(
        f"  Heading change during attack: "
        f"{heading_change:.2f} degrees"
    )

    print(
        f"  Speed change during attack: "
        f"{speed_change:.2f} km/h"
    )


print()
print(
    "Saved ->",
    OUTPUT_FILE
)