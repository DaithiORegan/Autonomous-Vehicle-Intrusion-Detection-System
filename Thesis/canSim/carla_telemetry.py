import carla
import csv
import math
import time
from pathlib import Path



HOST = "localhost"
PORT = 2000

DURATION_SECONDS = 60
SAMPLE_INTERVAL = 0.05

OUTPUT_FILE = Path("canSim/logs/carla_telemetry.csv")



print("=" * 70)
print("CARLA AUTONOMOUS VEHICLE TELEMETRY GENERATOR")
print("=" * 70)

client = carla.Client(HOST, PORT)
client.set_timeout(10.0)

world = client.get_world()

print(f"Connected to CARLA map: {world.get_map().name}")



settings = world.get_settings()

settings.no_rendering_mode = False

world.apply_settings(settings)

print(
    "No-rendering mode:",
    world.get_settings().no_rendering_mode
)



blueprint_library = world.get_blueprint_library()

tesla_blueprints = blueprint_library.filter(
    "vehicle.tesla.model3"
)

if not tesla_blueprints:
    raise RuntimeError(
        "Tesla Model 3 blueprint could not be found."
    )

vehicle_bp = tesla_blueprints[0]



spawn_points = world.get_map().get_spawn_points()

if not spawn_points:
    raise RuntimeError(
        "No vehicle spawn points were found."
    )



vehicle = None

for spawn_point in spawn_points:

    vehicle = world.try_spawn_actor(
        vehicle_bp,
        spawn_point
    )

    if vehicle is not None:
        break


if vehicle is None:
    raise RuntimeError(
        "Could not spawn Tesla Model 3."
    )


print(f"Vehicle spawned: {vehicle.type_id}")




vehicle.set_autopilot(True)

print("Autopilot enabled.")



spectator = world.get_spectator()

print("Spectator chase camera enabled.")




OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

print(f"Output file: {OUTPUT_FILE}")




print()
print(
    f"Collecting CARLA telemetry for "
    f"{DURATION_SECONDS} seconds..."
)
print()

start_time = time.time()


try:

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "can_id",
            "signal_name",
            "value",
            "label"
        ])


        while (
            time.time() - start_time
            < DURATION_SECONDS
        ):
            transform = vehicle.get_transform()

            forward = transform.get_forward_vector()

            camera_location = carla.Location(
                x=(
                    transform.location.x
                    - forward.x * 6.0
                ),
                y=(
                    transform.location.y
                    - forward.y * 6.0
                ),
                z=(
                    transform.location.z
                    + 3.0
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


            velocity = vehicle.get_velocity()

            speed_mps = math.sqrt(
                velocity.x ** 2
                + velocity.y ** 2
                + velocity.z ** 2
            )

            speed_kmh = speed_mps * 3.6


            control = vehicle.get_control()

            steering = control.steer
            brake = control.brake
            throttle = control.throttle



            timestamp = time.time()


   

            signals = [

                (
                    "0x100",
                    "vehicle_speed_kmh",
                    speed_kmh
                ),

                (
                    "0x101",
                    "steering_command",
                    steering
                ),

                (
                    "0x102",
                    "brake_command",
                    brake
                ),

                (
                    "0x103",
                    "throttle_command",
                    throttle
                )

            ]



            for (
                can_id,
                signal_name,
                value
            ) in signals:

                writer.writerow([
                    timestamp,
                    can_id,
                    signal_name,
                    round(value, 4),
                    0
                ])


        

            print(
                f"Speed {speed_kmh:6.2f} km/h | "
                f"Steer {steering:6.3f} | "
                f"Brake {brake:5.3f} | "
                f"Throttle {throttle:5.3f}"
            )


            time.sleep(
                SAMPLE_INTERVAL
            )


finally:

    print()
    print("Destroying vehicle...")

    if vehicle is not None:
        vehicle.destroy()


print()
print("=" * 70)
print("CARLA TELEMETRY COMPLETE")
print("=" * 70)

print(f"Saved: {OUTPUT_FILE}")