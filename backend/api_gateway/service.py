import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


AUTH_SERVICE_URL = "http://127.0.0.1:5001"


def forward_auth_request(method, path, data=None, authorization=None):
    url = f"{AUTH_SERVICE_URL}{path}"

    headers = {}

    if data is not None:
        headers["Content-Type"] = "application/json"

    if authorization:
        headers["Authorization"] = authorization

    request_data = None

    if data is not None:
        request_data = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=request_data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8")

            if not response_body:
                return {}, response.status

            return json.loads(response_body), response.status

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)
            return error_data, error.code
        except Exception:
            return {
                "message": "Auth Service returned an error."
            }, error.code

    except URLError:
        return {
            "message": "Auth Service is unavailable."
        }, 503

    except json.JSONDecodeError:
        return {
            "message": "Auth Service returned invalid JSON."
        }, 502

    except Exception:
        return {
            "message": "API Gateway request failed."
        }, 500

COURSE_SERVICE_URL = "http://127.0.0.1:5002"


def forward_course_request(method, path, data=None, authorization=None):
    url = f"{COURSE_SERVICE_URL}{path}"

    headers = {}

    if data is not None:
        headers["Content-Type"] = "application/json"

    if authorization:
        headers["Authorization"] = authorization

    request_data = None

    if data is not None:
        request_data = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=request_data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")

            if not response_body:
                return {}, response.status

            return json.loads(response_body), response.status

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return error_data, error.code

        except Exception:
            return {
                "message": "Course Service returned an error."
            }, error.code

    except URLError:
        return {
            "message": "Course Service is unavailable."
        }, 503

    except json.JSONDecodeError:
        return {
            "message": "Course Service returned invalid JSON."
        }, 502

    except Exception:
        return {
            "message": "API Gateway course request failed."
        }, 500

LESSON_SERVICE_URL = "http://127.0.0.1:5004"


def forward_lesson_request(method, path, data=None, authorization=None):
    url = f"{LESSON_SERVICE_URL}{path}"

    headers = {}

    if data is not None:
        headers["Content-Type"] = "application/json"

    if authorization:
        headers["Authorization"] = authorization

    request_data = None

    if data is not None:
        request_data = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=request_data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")

            if not response_body:
                return {}, response.status

            return json.loads(response_body), response.status

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return error_data, error.code

        except Exception:
            return {
                "message": "Lesson Service returned an error."
            }, error.code

    except URLError:
        return {
            "message": "Lesson Service is unavailable."
        }, 503

    except json.JSONDecodeError:
        return {
            "message": "Lesson Service returned invalid JSON."
        }, 502

    except Exception:
        return {
            "message": "API Gateway lesson request failed."
        }, 500

PROGRESS_SERVICE_URL = "http://127.0.0.1:5005"


def forward_progress_request(method, path, data=None, authorization=None):
    url = f"{PROGRESS_SERVICE_URL}{path}"

    headers = {}

    if data is not None:
        headers["Content-Type"] = "application/json"

    if authorization:
        headers["Authorization"] = authorization

    request_data = None

    if data is not None:
        request_data = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=request_data,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read().decode("utf-8")

            if not response_body:
                return {}, response.status

            return json.loads(response_body), response.status

    except HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            error_data = json.loads(error_body)

            return error_data, error.code

        except Exception:
            return {
                "message": "Progress Service returned an error."
            }, error.code

    except URLError:
        return {
            "message": "Progress Service is unavailable."
        }, 503

    except json.JSONDecodeError:
        return {
            "message": "Progress Service returned invalid JSON."
        }, 502

    except Exception:
        return {
            "message": "API Gateway progress request failed."
        }, 500