import carla
import csv
import math
import time
from pathlib import Path


# =========================================================
# CONFIGURATION
# =========================================================

HOST = "localhost"
PORT = 2000

NORMAL_DURATION = 15
ATTACK_DURATION = 4
POST_ATTACK_DURATION = 10

SAMPLE_INTERVAL = 0.05

# Strong visible steering command.
# CARLA steer ranges from -1.0 to +1.0.
ATTACK_STEER = 0.75

OUTPUT_FILE = Path(
    "canSim/logs/carla_visual_spoof.csv"
)


# =========================================================
# CONNECT
# =========================================================

print("=" * 70)
print("CARLA VISUAL CAN STEERING SPOOF DEMONSTRATION")
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


# =========================================================
# ENABLE RENDERING
# =========================================================

settings = world.get_settings()

settings.no_rendering_mode = False

world.apply_settings(settings)


# =========================================================
# SPAWN VEHICLE
# =========================================================

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
    "Vehicle:",
    vehicle.type_id
)


# =========================================================
# AUTOPILOT
# =========================================================

vehicle.set_autopilot(True)

print("Autopilot enabled.")


# =========================================================
# CHASE CAMERA
# =========================================================

spectator = world.get_spectator()


def update_camera():

    transform = vehicle.get_transform()

    forward = transform.get_forward_vector()

    camera_location = carla.Location(
        x=(
            transform.location.x
            - forward.x * 7
        ),
        y=(
            transform.location.y
            - forward.y * 7
        ),
        z=(
            transform.location.z
            + 3.5
        )
    )

    camera_rotation = carla.Rotation(
        pitch=-12,
        yaw=transform.rotation.yaw,
        roll=0
    )

    spectator.set_transform(
        carla.Transform(
            camera_location,
            camera_rotation
        )
    )


# =========================================================
# SPEED FUNCTION
# =========================================================

def get_speed():

    velocity = vehicle.get_velocity()

    return math.sqrt(
        velocity.x ** 2
        + velocity.y ** 2
        + velocity.z ** 2
    ) * 3.6


# =========================================================
# CSV
# =========================================================

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
    "speed_kmh",
    "steering",
    "brake",
    "throttle",
    "attack_active",
    "attack_type"
])


# =========================================================
# PHASE 1 - NORMAL DRIVING
# =========================================================

print()
print("=" * 70)
print("PHASE 1 - NORMAL AUTONOMOUS DRIVING")
print("=" * 70)

start = time.time()

try:

    while (
        time.time() - start
        < NORMAL_DURATION
    ):

        update_camera()

        control = vehicle.get_control()

        speed = get_speed()

        writer.writerow([
            time.time(),
            speed,
            control.steer,
            control.brake,
            control.throttle,
            0,
            "benign"
        ])

        print(
            f"NORMAL | "
            f"Speed {speed:6.2f} km/h | "
            f"Steer {control.steer:6.3f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )


    # =====================================================
    # PHASE 2 - ATTACK
    # =====================================================

    print()
    print("!" * 70)
    print("STEERING SPOOF ATTACK ACTIVE")
    print("!" * 70)

    # Traffic Manager owns the vehicle while autopilot
    # is enabled, so disable autopilot before manually
    # applying the spoofed control.
    vehicle.set_autopilot(False)

    attack_start = time.time()

    while (
        time.time() - attack_start
        < ATTACK_DURATION
    ):

        update_camera()

        current = vehicle.get_control()

        malicious_control = carla.VehicleControl(
            throttle=max(
                current.throttle,
                0.35
            ),
            steer=ATTACK_STEER,
            brake=0.0
        )

        vehicle.apply_control(
            malicious_control
        )

        speed = get_speed()

        writer.writerow([
            time.time(),
            speed,
            ATTACK_STEER,
            0.0,
            malicious_control.throttle,
            1,
            "steering_spoof"
        ])

        print(
            f">>> ATTACK | "
            f"Speed {speed:6.2f} km/h | "
            f"SPOOFED STEER {ATTACK_STEER:5.2f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )


    # =====================================================
    # PHASE 3 - RESTORE AUTOPILOT
    # =====================================================

    print()
    print("=" * 70)
    print("ATTACK ENDED - RESTORING AUTOPILOT")
    print("=" * 70)

    vehicle.set_autopilot(True)

    recovery_start = time.time()

    while (
        time.time() - recovery_start
        < POST_ATTACK_DURATION
    ):

        update_camera()

        control = vehicle.get_control()

        speed = get_speed()

        writer.writerow([
            time.time(),
            speed,
            control.steer,
            control.brake,
            control.throttle,
            0,
            "benign"
        ])

        print(
            f"RECOVERY | "
            f"Speed {speed:6.2f} km/h | "
            f"Steer {control.steer:6.3f}"
        )

        time.sleep(
            SAMPLE_INTERVAL
        )


finally:

    print()
    print("Demo complete.")

    file.close()

    if vehicle is not None:
        vehicle.destroy()


print(
    "Saved ->",
    OUTPUT_FILE
)