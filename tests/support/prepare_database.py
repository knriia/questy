import subprocess
from shutil import which

from dotenv import dotenv_values
from sqlalchemy.dialects.postgresql import dialect

TEST_ENV_FILE = ".env.test"


def main() -> None:
    values = dotenv_values(TEST_ENV_FILE)
    username = values.get("DB_USER")
    password = values.get("DB_PASSWORD")
    if not username or not password:
        raise SystemExit("Set DB_USER and DB_PASSWORD in .env.test")

    docker = which("docker")
    if docker is None:
        raise SystemExit("Docker is required to prepare the test role")
    quoted_username = dialect().identifier_preparer.quote_identifier(username)
    quoted_password = "'" + password.replace("'", "''") + "'"
    statement = (
        "SET standard_conforming_strings = on;\n"
        f"CREATE ROLE {quoted_username} LOGIN PASSWORD {quoted_password} "
        "NOSUPERUSER CREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;\n"
    )
    result = subprocess.run(  # noqa: S603
        [
            docker,
            "compose",
            "exec",
            "-T",
            "postgres",
            "sh",
            "-c",
            'exec psql -X --set=ON_ERROR_STOP=1 --username="$POSTGRES_USER" --dbname=postgres',
        ],
        input=statement,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise SystemExit(
            "Cannot create test role: check that PostgreSQL is running and the role does not already exist."
        )
    print("Test PostgreSQL role created.")


if __name__ == "__main__":
    main()
