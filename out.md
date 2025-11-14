============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-9.0.1, pluggy-1.6.0
rootdir: /Users/gabrielrabelomoura/Desktop/Crossmint/Learning
plugins: anyio-4.11.0
collected 30 items

test_api.py ..F........F.F.F.F...F.F.F.F..                               [100%]

=================================== FAILURES ===================================
_________________________ test_list_libraries_success __________________________

client_and_service = <starlette.testclient.TestClient object at 0x109f3fc50>

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
E                 {'type': 'list_type', 'loc': ('response',), 'msg': 'Input should be a valid list', 'input': {'libraries': [{'id': 'c1a55d13-1edc-4910-af08-922243fefc62', 'name': 'lib1'}]}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
_________________________ test_list_documents_success __________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a5349b0>

    def test_list_documents_success(client_and_service):
        doc = {"id": str(uuid.uuid4()), "title": "doc1"}
        main.service.list_documents_return = [doc]
        lib_id = str(uuid.uuid4())
>       resp = client_and_service.get(f"/libraries/{lib_id}/documents")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:207: 
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
E                 {'type': 'list_type', 'loc': ('response',), 'msg': 'Input should be a valid list', 'input': {'documents': [{'id': '72dd6f9f-c989-424a-b56a-8a1a43ca5c9c', 'title': 'doc1'}]}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
__________________________ test_get_document_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a54af90>

    def test_get_document_success(client_and_service):
        doc = {"id": str(uuid.uuid4()), "title": "docX"}
        main.service.get_document_return = doc
        lib_id = str(uuid.uuid4())
>       resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc['id']}")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:225: 
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
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'document': {'id': 'f9826762-69fd-4b84-9d00-4f17f1ed5aa1', 'title': 'docX'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
_________________________ test_create_document_success _________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a62dfd0>

    def test_create_document_success(client_and_service):
        lib_id = str(uuid.uuid4())
        created_doc = {"id": str(uuid.uuid4()), "title": "created"}
        main.service.create_document_return = created_doc
>       resp = client_and_service.post(
            f"/libraries/{lib_id}/documents", json={"title": created_doc["title"]}
        )

test_api.py:243: 
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
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'document': {'id': 'ca4e24e8-471f-48ce-acaf-83da359bf358', 'title': 'created'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
_________________________ test_update_document_success _________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a54ac10>

    def test_update_document_success(client_and_service):
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        updated = {"id": doc_id, "title": "updated"}
        main.service.update_document_return = updated
>       resp = client_and_service.put(
            f"/libraries/{lib_id}/documents/{doc_id}", json={"title": updated["title"]}
        )

test_api.py:266: 
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
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'document': {'id': '7ef3a78e-522c-411c-9900-eed160b0602a', 'title': 'updated'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
___________________________ test_list_chunks_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a52ef90>

    def test_list_chunks_success(client_and_service):
        chunk = {"id": str(uuid.uuid4()), "text": "c"}
        main.service.list_chunks_return = [chunk]
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
>       resp = client_and_service.get(f"/libraries/{lib_id}/documents/{doc_id}/chunks")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

test_api.py:309: 
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
E                 {'type': 'list_type', 'loc': ('response',), 'msg': 'Input should be a valid list', 'input': {'chunks': [{'id': '28cd3be4-35f1-46ed-8348-26bd7136e0af', 'text': 'c'}]}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
____________________________ test_get_chunk_success ____________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a52e190>

    def test_get_chunk_success(client_and_service):
        chunk = {"id": str(uuid.uuid4()), "text": "chunk"}
        main.service.get_chunk_return = chunk
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
>       resp = client_and_service.get(
            f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk['id']}"
        )

test_api.py:331: 
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
E               fastapi.exceptions.ResponseValidationError: 2 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'document_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': 'b498edbe-2ee4-4481-9839-72b80dd58748', 'text': 'chunk'}}}
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': 'b498edbe-2ee4-4481-9839-72b80dd58748', 'text': 'chunk'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
__________________________ test_create_chunk_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a55fcb0>

    def test_create_chunk_success(client_and_service):
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        created = {"id": str(uuid.uuid4()), "text": "created"}
        main.service.create_chunk_return = created
>       resp = client_and_service.post(
            f"/libraries/{lib_id}/documents/{doc_id}/chunks", json={"text": created["text"]}
        )

test_api.py:354: 
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
E               fastapi.exceptions.ResponseValidationError: 2 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'document_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': 'b533c34c-392f-415a-8b56-af539bc656de', 'text': 'created'}}}
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': 'b533c34c-392f-415a-8b56-af539bc656de', 'text': 'created'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
__________________________ test_update_chunk_success ___________________________

client_and_service = <starlette.testclient.TestClient object at 0x10a571ef0>

    def test_update_chunk_success(client_and_service):
        lib_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        chunk_id = str(uuid.uuid4())
        updated = {"id": chunk_id, "text": "updated"}
        main.service.update_chunk_return = updated
>       resp = client_and_service.put(
            f"/libraries/{lib_id}/documents/{doc_id}/chunks/{chunk_id}",
            json={"text": "updated"},
        )

test_api.py:379: 
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
E               fastapi.exceptions.ResponseValidationError: 2 validation errors:
E                 {'type': 'missing', 'loc': ('response', 'document_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': '8f3deaf8-3c48-48eb-a1ef-0beb6d378a64', 'text': 'updated'}}}
E                 {'type': 'missing', 'loc': ('response', 'library_uid'), 'msg': 'Field required', 'input': {'chunk': {'id': '8f3deaf8-3c48-48eb-a1ef-0beb6d378a64', 'text': 'updated'}}}

.venv/lib/python3.13/site-packages/fastapi/routing.py:254: ResponseValidationError
=========================== short test summary info ============================
FAILED test_api.py::test_list_libraries_success - fastapi.exceptions.Response...
FAILED test_api.py::test_list_documents_success - fastapi.exceptions.Response...
FAILED test_api.py::test_get_document_success - fastapi.exceptions.ResponseVa...
FAILED test_api.py::test_create_document_success - fastapi.exceptions.Respons...
FAILED test_api.py::test_update_document_success - fastapi.exceptions.Respons...
FAILED test_api.py::test_list_chunks_success - fastapi.exceptions.ResponseVal...
FAILED test_api.py::test_get_chunk_success - fastapi.exceptions.ResponseValid...
FAILED test_api.py::test_create_chunk_success - fastapi.exceptions.ResponseVa...
FAILED test_api.py::test_update_chunk_success - fastapi.exceptions.ResponseVa...
========================= 9 failed, 21 passed in 2.42s =========================
