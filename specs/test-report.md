# Reporte de Pruebas de Software (Test Report)

- **Proyecto ID:** QFAI
- **Suite:** Pytest (FastAPI TestClient)
- **Entorno de Aislamiento:** Sandbox Local

## Resultado
- **Estado General:** FAIL

### Pytest Sandbox Execution Log
```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: C:\\Users\\anton\\Downloads\\Fabrica BA\u0301SICA APP WEB 15.46.51\\Fabrica BA\u2560\xfcSICA APP WEB
configfile: pytest.ini
plugins: anyio-4.10.0
collected 2 items

tests\test_main.py ..E                                                   [100%]

=================================== ERRORS ====================================
______________ ERROR at teardown of test_panorama_crud_and_join _______________

    @pytest.fixture(scope="module", autouse=True)
    def setup_db():
        Base.metadata.create_all(bind=engine)
        yield
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./qfai_test.db"):
>           os.remove("./qfai_test.db")
E           PermissionError: [WinError 32] El proceso no tiene acceso al archivo porque está siendo utilizado por otro proceso: './qfai_test.db'

tests\test_main.py:19: PermissionError
============================== warnings summary ===============================
D:\Anaconda\2\Lib\site-packages\fastapi\testclient.py:1
  D:\Anaconda\2\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

app\main.py:16
  C:\\Users\\anton\\Downloads\\Fabrica BA\u0301SICA APP WEB 15.46.51\\Fabrica BA\u2560\xfcSICA APP WEB\\sandbox\\QFAI\\backend\\app\\main.py:16: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)\n    Base = declarative_base()

app\main.py:104
  C:\\Users\\anton\\Downloads\\Fabrica BA\u0301SICA APP WEB 15.46.51\\Fabrica BA\u2560\xfcSICA APP WEB\\sandbox\\QFAI\\backend\\app\\main.py:104: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/\n    class UserResponse(BaseModel):

app\main.py:121
  C:\\Users\\anton\\Downloads\\Fabrica BA\u0301SICA APP WEB 15.46.51\\Fabrica BA\u2560\xfcSICA APP WEB\\sandbox\\QFAI\\backend\\app\\main.py:121: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.12/migration/\n    class PanoramaResponse(BaseModel):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests\test_main.py::test_panorama_crud_and_join - PermissionError: [Win...
=================== 2 passed, 4 warnings, 1 error in 5.47s ====================


```