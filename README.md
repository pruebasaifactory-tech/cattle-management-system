# Sistema de Gestión Ganadera

## 🚀 Inicio Rápido
1. Clona este repositorio y entra al directorio raíz.
2. Copia `backend/.env.example` a `backend/.env` y ajusta credenciales de base de datos.
3. Ejecuta `./run.sh` (Linux/Mac) o `run.bat` (Windows) para levantar toda la pila mediante Docker en cuanto esos scripts estén disponibles en la fase de despliegue.
4. Mientras tanto, puedes iniciar el backend localmente con `uvicorn app.main:app --reload` desde la carpeta `backend` para validar los servicios creados en esta iteración.

> ⏱️ Tiempo estimado del primer arranque con Docker (cuando esté habilitado): 3-4 minutos, incluye descarga de imágenes y build inicial.
> 🌐 Servicios previstos: API FastAPI en `http://localhost:8000`, base de datos PostgreSQL en `localhost:5432`.

## 🧭 Descripción
Plataforma modular para registrar, gestionar y reportar la información sanitaria y productiva del hato bovino. El backend está diseñado en FastAPI siguiendo un enfoque de microservicios (autenticación, gestión de ganado y reportes) y se integra con PostgreSQL 15. El objetivo a largo plazo es exponer APIs seguras basadas en JWT, sincronizar operaciones offline y automatizar la generación de reportes exportables.

## 🛠️ Stack Tecnológico
- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL 15
- Pydantic para validaciones
- JWT (python-jose) y Passlib para autenticación
- Docker & Docker Compose (fase de despliegue)
- Angular 17 (frontend, planificado)

## 📂 Estructura del Proyecto (Parcial)
```
backend/
  app/
    __init__.py
    core/
      __init__.py
  requirements.txt
  pyproject.toml
  .env.example
  .gitignore
README.md
```
Esta estructura crecerá para incluir microservicios independientes (`app/api`, `app/services`, `app/models`) y la aplicación Angular dentro de `frontend/`.

## ⚙️ Configuración
1. **Variables de entorno:** usa `backend/.env.example` como plantilla. Define conexión a PostgreSQL, claves JWT y configuraciones de servicio.
2. **Dependencias Python:** ejecuta `pip install -r backend/requirements.txt` desde un virtualenv basado en Python 3.11.
3. **Formato y estilo:** el proyecto seguirá convenciones PEP8 y aplicará tipado estático opcional (mypy) en fases posteriores.

## 📡 Servicios Planeados
- **Auth Service:** registro, login y emisión de JWT.
- **Cattle Service:** CRUD completo de ganado, registros de salud y peso.
- **Reports Service:** generación y descarga de reportes CSV/JSON.
- **Sync Service:** conciliación de operaciones offline.

Cada servicio tendrá routers dedicados, esquemas Pydantic y repositorios SQLAlchemy. Esta iteración sólo abarca la capa base y dependencias.

## 🧪 Pruebas y Calidad
Por lineamientos de este entregable no se incluyen suites de prueba automatizadas. Las verificaciones se realizan ejecutando manualmente `uvicorn` y validando que `pip install -r backend/requirements.txt` concluya sin errores.

## 🔐 Seguridad y Credenciales
- Usa contraseñas únicas para PostgreSQL y nunca comprometas secretos en el repositorio.
- Variables sensibles se cargan desde `.env`; el archivo está excluido mediante `.gitignore`.
- JWT usará claves firmadas definidas en `SECRET_KEY`.

## 📈 Roadmap Inmediato
1. Modelado de base de datos y configuración SQLAlchemy.
2. Implementación del microservicio de autenticación.
3. CRUD de ganado y registros.
4. Reportes, sincronización offline y despliegue Docker/Angular.

## 📚 Referencias
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Docker Docs](https://docs.docker.com/)

