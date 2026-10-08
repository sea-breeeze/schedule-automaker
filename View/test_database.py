from database import update_worker, get_workers

print("Before UPDATE:")
for worker in get_workers():
    print(worker)

updated = update_worker(
    "UpdateTest",
    ["Thu", "Fri"]
)

print("Workers updated:", updated)

print("After UPDATE:")
for worker in get_workers():
    print(worker)