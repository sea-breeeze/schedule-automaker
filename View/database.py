import sqlite3


def create_database():
    connection = sqlite3.connect("schedule.db")

    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS worker_availability (
            worker_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            PRIMARY KEY (worker_id, day),
            FOREIGN KEY (worker_id)
                REFERENCES workers(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            duration INTEGER NOT NULL CHECK (duration > 0),
            rotating INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()
    
def add_worker(name, availability):
    connection = sqlite3.connect("schedule.db")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = connection.cursor()

        # Insert the worker's name
        cursor.execute(
            "INSERT INTO workers (name) VALUES (?)",
            (name,)
        )

        # Get the ID of the worker we just inserted
        worker_id = cursor.lastrowid

        # Insert each available day
        for day in availability:
            cursor.execute(
                """
                INSERT INTO worker_availability (worker_id, day)
                VALUES (?, ?)
                """,
                (worker_id, day)
            )

        connection.commit()
        return worker_id

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def get_workers():
    connection = sqlite3.connect("schedule.db")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                workers.id,
                workers.name,
                worker_availability.day
            FROM workers
            LEFT JOIN worker_availability
                ON workers.id = worker_availability.worker_id
            ORDER BY workers.id, worker_availability.day
        """)

        rows = cursor.fetchall()

        workers = {}

        for worker_id, name, day in rows:

            if worker_id not in workers:
                workers[worker_id] = {
                    "name": name,
                    "availability": []
                }

            if day is not None:
                workers[worker_id]["availability"].append(day)

        return list(workers.values())

    finally:
        connection.close()
        
def add_task(name, duration, rotating):
    connection = sqlite3.connect("schedule.db")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks (name, duration, rotating)
            VALUES (?, ?, ?)
            """,
            (name, duration, int(rotating))
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def get_tasks():
    connection = sqlite3.connect("schedule.db")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name, duration, rotating
            FROM tasks
            ORDER BY id
        """)

        rows = cursor.fetchall()

        tasks = []

        for name, duration, rotating in rows:
            task = {
                "name": name,
                "duration": duration,
                "rotating": bool(rotating)
            }

            tasks.append(task)

        return tasks

    finally:
        connection.close()
        
def update_task(name, duration, rotating):
    connection = sqlite3.connect("schedule.db")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET duration = ?, rotating = ?
            WHERE name = ?
            """,
            (duration, int(rotating), name)
        )

        connection.commit()
        return cursor.rowcount

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def delete_task(name):
    connection = sqlite3.connect("schedule.db")

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE name = ?",
            (name,)
        )

        connection.commit()
        return cursor.rowcount

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        
def delete_worker(name):
    connection = sqlite3.connect("schedule.db")

    # SQLite requires foreign keys to be enabled
    # for each new connection.
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM workers WHERE name = ?",
            (name,)
        )

        connection.commit()
        return cursor.rowcount

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()
        
        
def update_worker(name, availability):
    connection = sqlite3.connect("schedule.db")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        cursor = connection.cursor()

        # Find the worker's ID
        cursor.execute(
            "SELECT id FROM workers WHERE name = ?",
            (name,)
        )

        result = cursor.fetchone()

        if result is None:
            return 0

        worker_id = result[0]

        # Delete the worker's previous availability
        cursor.execute(
            "DELETE FROM worker_availability WHERE worker_id = ?",
            (worker_id,)
        )

        # Insert the new availability
        for day in availability:
            cursor.execute(
                """
                INSERT INTO worker_availability (worker_id, day)
                VALUES (?, ?)
                """,
                (worker_id, day)
            )

        connection.commit()
        return 1

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()