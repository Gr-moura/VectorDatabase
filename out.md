============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.0.1, pluggy-1.6.0
rootdir: /Users/gabrielrabelomoura/Desktop/Crossmint/Learning
plugins: anyio-4.11.0
collected 30 items

test_api.py .FF.FF.F..FF.....F..FF........                               [100%]

=================================== FAILURES ===================================
________________________ test_list_libraries_not_found _________________________

client_and_service = <starlette.testclient.TestClient object at 0x1081a6210>

    def test_list_libraries_not_found(client_and_service):
        # service.list_libraries returns falsy => 404
        main.service.list_libraries_return = []
        resp = client_and_service.get("/libraries")
>       assert resp.status_code == 404
E       assert 200 == 404
E        +  where 200 = <Response [200 OK]>.status_code

test_api.py:114: AssertionError
_________________________ test_list_libraries_success __________________________

client_and_service = <starlette.testclient.TestClient object at 0x106e90cd0>

    def test_list_libraries_success(client_and_service):
        lib = {"id": str(uuid.uuid4()), "name": "lib1"}
        main.service.list_libraries_return = [lib]
>       resp = client_and_service.get("/libraries")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:121: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.13/site-packages/starlette/testclient.py:479: in get
    return super().get(
.venv/lib/python3.13/site-packages/httpx/_client.py:1053: in get
    return self.request(
.venv/lib/python3.13/site-packages/starlette/testclient.py:451: in request
    return super().request(
.venv/lib/python3.13/site-packages/httpx/_client.py:825: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
.venv/lib/python3.13/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
.venv/lib/python3.13/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:1014: in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/starlette/testclient.py:354: in handle_request
    raise exc
.venv/lib/python3.13/site-packages/starlette/testclient.py:351: in handle_request
    portal.call(self.app, scope, receive, send)
.venv/lib/python3.13/site-packages/anyio/from_thread.py:321: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:456: in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
.venv/lib/python3.13/site-packages/anyio/from_thread.py:252: in _call_func
    retval = await retval_or_awaitable
             ^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/applications.py:1134: in __call__
    await super().__call__(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:290: in handle
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/fastapi/routing.py:125: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/routing.py:111: in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/routing.py:413: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 1 validation errors:
E                 {'type': 'missing', 'loc': ('response', 0, 'library'), 'msg': 'Field required', 'input': {'id': 'd7765dac-c15d-41b0-837e-a69b84b30e9d', 'name': 'lib1'}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
___________________________ test_get_library_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x1082e2520>

    def test_get_library_success(client_and_service):
        lib = {"id": str(uuid.uuid4()), "name": "libX"}
        main.service.get_library_return = lib
>       resp = client_and_service.get(f"/libraries/{lib['id']}")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:139: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.13/site-packages/starlette/testclient.py:479: in get
    return super().get(
.venv/lib/python3.13/site-packages/httpx/_client.py:1053: in get
    return self.request(
.venv/lib/python3.13/site-packages/starlette/testclient.py:451: in request
    return super().request(
.venv/lib/python3.13/site-packages/httpx/_client.py:825: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
.venv/lib/python3.13/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
.venv/lib/python3.13/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:1014: in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/starlette/testclient.py:354: in handle_request
    raise exc
.venv/lib/python3.13/site-packages/starlette/testclient.py:351: in handle_request
    portal.call(self.app, scope, receive, send)
.venv/lib/python3.13/site-packages/anyio/from_thread.py:321: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:456: in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
.venv/lib/python3.13/site-packages/anyio/from_thread.py:252: in _call_func
    retval = await retval_or_awaitable
             ^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/applications.py:1134: in __call__
    await super().__call__(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:290: in handle
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/fastapi/routing.py:125: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/routing.py:111: in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/routing.py:413: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 1 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'library'), 'msg': 'Field required', 'input': {'id': '7d84b8fa-1c33-4c99-8bf5-6fd186e4fa55', 'name': 'libX'}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
_____________________________ test_create_library ______________________________

client_and_service = <starlette.testclient.TestClient object at 0x1081f1910>

    def test_create_library(client_and_service):
        payload = {"name": "new lib"}
        created = {"id": str(uuid.uuid4()), "name": payload["name"]}
        main.service.create_library_return = created
>       resp = client_and_service.post("/libraries", json=payload)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:148: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.13/site-packages/starlette/testclient.py:552: in post
    return super().post(
.venv/lib/python3.13/site-packages/httpx/_client.py:1144: in post
    return self.request(
.venv/lib/python3.13/site-packages/starlette/testclient.py:451: in request
    return super().request(
.venv/lib/python3.13/site-packages/httpx/_client.py:825: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
.venv/lib/python3.13/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
.venv/lib/python3.13/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:1014: in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/starlette/testclient.py:354: in handle_request
    raise exc
.venv/lib/python3.13/site-packages/starlette/testclient.py:351: in handle_request
    portal.call(self.app, scope, receive, send)
.venv/lib/python3.13/site-packages/anyio/from_thread.py:321: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:456: in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
.venv/lib/python3.13/site-packages/anyio/from_thread.py:252: in _call_func
    retval = await retval_or_awaitable
             ^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/applications.py:1134: in __call__
    await super().__call__(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:290: in handle
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/fastapi/routing.py:125: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/routing.py:111: in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/routing.py:413: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 1 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'library'), 'msg': 'Field required', 'input': {'id': 'cd1d7c1d-9c0e-4300-80f7-07d9a4e19244', 'name': 'new lib'}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
_________________________ test_update_library_success __________________________

client_and_service = <starlette.testclient.TestClient object at 0x1088906b0>

    def test_update_library_success(client_and_service):
        lib_id = str(uuid.uuid4())
        updated = {"id": lib_id, "name": "updated name"}
        main.service.update_library_return = updated
>       resp = client_and_service.put(
            f"/libraries/{lib_id}", json={"name": updated["name"]}
        )

test_api.py:166: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
.venv/lib/python3.13/site-packages/starlette/testclient.py:583: in put
    return super().put(
.venv/lib/python3.13/site-packages/httpx/_client.py:1181: in put
    return self.request(
.venv/lib/python3.13/site-packages/starlette/testclient.py:451: in request
    return super().request(
.venv/lib/python3.13/site-packages/httpx/_client.py:825: in request
    return self.send(request, auth=auth, follow_redirects=follow_redirects)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:914: in send
    response = self._send_handling_auth(
.venv/lib/python3.13/site-packages/httpx/_client.py:942: in _send_handling_auth
    response = self._send_handling_redirects(
.venv/lib/python3.13/site-packages/httpx/_client.py:979: in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/httpx/_client.py:1014: in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/starlette/testclient.py:354: in handle_request
    raise exc
.venv/lib/python3.13/site-packages/starlette/testclient.py:351: in handle_request
    portal.call(self.app, scope, receive, send)
.venv/lib/python3.13/site-packages/anyio/from_thread.py:321: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:456: in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.13/3.13.7/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py:401: in __get_result
    raise self._exception
.venv/lib/python3.13/site-packages/anyio/from_thread.py:252: in _call_func
    retval = await retval_or_awaitable
             ^^^^^^^^^^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/applications.py:1134: in __call__
    await super().__call__(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:186: in __call__
    raise exc
.venv/lib/python3.13/site-packages/starlette/middleware/errors.py:164: in __call__
    await self.app(scope, receive, _send)
.venv/lib/python3.13/site-packages/starlette/middleware/exceptions.py:63: in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/middleware/asyncexitstack.py:18: in __call__
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:716: in __call__
    await self.middleware_stack(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:736: in app
    await route.handle(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/routing.py:290: in handle
    await self.app(scope, receive, send)
.venv/lib/python3.13/site-packages/fastapi/routing.py:125: in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:53: in wrapped_app
    raise exc
.venv/lib/python3.13/site-packages/starlette/_exception_handler.py:42: in wrapped_app
    await app(scope, receive, sender)
.venv/lib/python3.13/site-packages/fastapi/routing.py:111: in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
.venv/lib/python3.13/site-packages/fastapi/routing.py:413: in app
    content = await serialize_response(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

    async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[IncEx] = None,
        exclude: Optional[IncEx] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
    ) -> Any:
        if field:
            errors = []
            if not hasattr(field, "serialize"):
                # pydantic v1
                response_content = _prepare_response_content(
                    response_content,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, list):
                errors.extend(errors_)
            elif errors_:
                errors.append(errors_)
            if errors:
>               raise ResponseValidationError(
                    errors=_normalize_errors(errors), body=response_content
                )
E               fastapi.exceptions.ResponseValidationError: 1 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'library'), 'msg': 'Field required', 'input': {'id': '9e9f9ff3-c90e-45f4-bce2-49f5bbd006be', 'name': 'updated name'}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
________________________ test_list_documents_not_found _________________________

client_and_service = <starlette.testclient.TestClient object at 0x1088b8f50>

    def test_list_documents_not_found(client_and_service):
        main.service.list_documents_return = []
        lib_id = str(uuid.uuid4())
        resp = client_and_service.get(f"/libraries/{lib_id}/documents")
>       assert resp.status_code == 404
E       assert 200 == 404
E        +  where 200 = <Response [200 OK]>.status_code

test_api.py:199: AssertionError
_________________________ test_list_documents_success __________________________

client_and_service = <starlette.testclient.TestClient object at 0x10884b020>

    def test_list_documents_success(client_and_service):
        doc = {"id": str(uuid.uuid4()), "title": "doc1"}
        main.service.list_documents_return = [doc]
        lib_id = str(uuid.uuid4())
        resp = client_and_service.get(f"/libraries/{lib_id}/documents")
        assert resp.status_code == 200
>       assert resp.json()["documents"][0]["id"] == doc["id"]
               ^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: list indices must be integers or slices, not str

test_api.py:209: TypeError
_________________________ test_update_document_success _________________________

client_and_service = <starlette.testclient.TestClient object at 0x1088af310>

    def test_update_document_success(client_and_service):
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        updated = {"id": doc_id, "title": "updated"}
        main.service.update_document_return = updated
        resp = client_and_service.put(
            f"/libraries/{lib_id}/documents/{doc_id}", json={"title": updated["title"]}
        )
        assert resp.status_code == 200
>       assert resp.json()["document"]["title"] == "updated"
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'title'

test_api.py:270: KeyError
__________________________ test_list_chunks_not_found __________________________

client_and_service = <starlette.testclient.TestClient object at 0x1088ac9f0>

    def test_list_chunks_not_found(client_and_service):
        main.service.list_chunks_return = []
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
>       assert resp.status_code == 404
E       assert 200 == 404
E        +  where 200 = <Response [200 OK]>.status_code

test_api.py:300: AssertionError
___________________________ test_list_chunks_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x1088ae5f0>

    def test_list_chunks_success(client_and_service):
        chunk = {"id": str(uuid.uuid4()), "text": "c"}
        main.service.list_chunks_return = [chunk]
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
        assert resp.status_code == 200
>       assert resp.json()["chunks"][0]["id"] == chunk["id"]
               ^^^^^^^^^^^^^^^^^^^^^
E       TypeError: list indices must be integers or slices, not str

test_api.py:311: TypeError
=========================== short test summary info ============================
FAILED test_api.py::test_list_libraries_not_found - assert 200 == 404
FAILED test_api.py::test_list_libraries_success - fastapi.exceptions.Response...
FAILED test_api.py::test_get_library_success - fastapi.exceptions.ResponseVal...
FAILED test_api.py::test_create_library - fastapi.exceptions.ResponseValidati...
FAILED test_api.py::test_update_library_success - fastapi.exceptions.Response...
FAILED test_api.py::test_list_documents_not_found - assert 200 == 404
FAILED test_api.py::test_list_documents_success - TypeError: list indices mus...
FAILED test_api.py::test_update_document_success - KeyError: 'title'
FAILED test_api.py::test_list_chunks_not_found - assert 200 == 404
FAILED test_api.py::test_list_chunks_success - TypeError: list indices must b...
======================== 10 failed, 20 passed in 1.36s =========================
