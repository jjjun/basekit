from basekit.docker_compose import (
    DockerComposeGenerator,
    DockerService,
    DockerVolume,
)


def test_create_minimal_service():
    service = DockerService(
        name="postgres",
        image="postgres:16-alpine",
        container_name="test_postgres",
    )

    assert service.name == "postgres"
    assert service.image == "postgres:16-alpine"
    assert service.container_name == "test_postgres"
    assert service.ports == []


def test_generate_minimal_compose():
    generator = DockerComposeGenerator()
    generator.add_service(
        DockerService(
            name="postgres",
            image="postgres:16-alpine",
            container_name="test_postgres",
        )
    )

    yaml_content = generator.generate()

    assert "version: '3.8'" in yaml_content
    assert "services:" in yaml_content
    assert "  postgres:" in yaml_content
    assert "    image: postgres:16-alpine" in yaml_content
    assert "    container_name: test_postgres" in yaml_content


def test_generate_compose_with_common_service_fields():
    generator = DockerComposeGenerator(version="3.9")
    service = DockerService(
        name="postgres",
        image="postgres:16-alpine",
        container_name="test_postgres",
        ports=["5432:5432"],
        environment={"POSTGRES_USER": "user", "POSTGRES_PASSWORD": "pass"},
        volumes=["postgres_data:/var/lib/postgresql/data"],
        healthcheck={
            "test": '["CMD-SHELL", "pg_isready -U user"]',
            "interval": "5s",
        },
    )

    generator.add_service(service).add_volume(DockerVolume(name="postgres_data"))
    yaml_content = generator.generate()

    assert "version: '3.9'" in yaml_content
    assert "      POSTGRES_USER: user" in yaml_content
    assert '      - "5432:5432"' in yaml_content
    assert "      - postgres_data:/var/lib/postgresql/data" in yaml_content
    assert '      test: ["CMD-SHELL", "pg_isready -U user"]' in yaml_content
    assert "  postgres_data:" in yaml_content


def test_generate_compose_with_depends_on():
    generator = DockerComposeGenerator()
    generator.add_service(
        DockerService(
            name="app",
            image="app:latest",
            container_name="test_app",
            depends_on={"postgres": {"condition": "service_healthy"}},
        )
    )

    yaml_content = generator.generate()

    assert "    depends_on:" in yaml_content
    assert "      postgres:" in yaml_content
    assert "        condition: service_healthy" in yaml_content


def test_write_to_file(tmp_path):
    generator = DockerComposeGenerator()
    generator.add_service(
        DockerService(
            name="postgres",
            image="postgres:16-alpine",
            container_name="test_postgres",
        )
    )

    output_path = tmp_path / "docker-compose.yml"
    generator.write_to_file(output_path)

    assert output_path.exists()
    assert "  postgres:" in output_path.read_text(encoding="utf-8")
