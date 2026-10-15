import os
from datetime import datetime

import requests

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)

from agent.actions import (
    start_service,
    stop_service,
)

from agent.sre_agent import (
    run_sre_agent,
)

from agent.tools import (
    list_services,
    get_service_status,
    get_service_logs,
    check_service_dependencies,
    check_mysql_database,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder="showcase/templates",
    static_folder="showcase/static",
)


# ============================================================
# SERVICE INFORMATION
# ============================================================

SERVICE_INFO = {

    "meter-data-service": {

        "display_name": "Meter Data Service",

        "short_name": "Meter Data",

        "port": 3000,

        "technology": "Node.js / Express",

        "database": "MongoDB",

        "description": (
            "Collects and stores electricity meter "
            "readings used by Billing and Prediction."
        ),

        "mysql": False,
    },


    "billing-service": {

        "display_name": "Billing Service",

        "short_name": "Billing",

        "port": 3001,

        "technology": "Node.js / Express",

        "database": "MySQL · billing_db",

        "description": (
            "Uses electricity consumption data to "
            "generate customer electricity bills."
        ),

        "mysql": True,
    },


    "prediction-service": {

        "display_name": "Prediction Service",

        "short_name": "Prediction",

        "port": 3002,

        "technology": "Node.js / Express",

        "database": "MySQL · prediction_db",

        "description": (
            "Analyzes previous electricity usage and "
            "predicts future energy consumption."
        ),

        "mysql": True,
    },


    "user-service": {

        "display_name": "User Service",

        "short_name": "Users",

        "port": 8081,

        "technology": "Spring Boot",

        "database": "MySQL · user_db",

        "description": (
            "Manages system users, customer accounts "
            "and user information."
        ),

        "mysql": True,
    },
}


# ============================================================
# SERVICE URLS
# ============================================================

METER_URL = os.getenv(
    "METER_SERVICE_URL",
    "http://localhost:3000",
)

BILLING_URL = os.getenv(
    "BILLING_SERVICE_URL",
    "http://localhost:3001",
)

PREDICTION_URL = os.getenv(
    "PREDICTION_SERVICE_URL",
    "http://localhost:3002",
)

USER_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://localhost:8081",
)


DATA_ENDPOINTS = {

    "usage":
        METER_URL
        + "/api/usage",

    "bills":
        BILLING_URL
        + "/api/bills",

    "predictions":
        PREDICTION_URL
        + "/api/predictions",

    "users":
        USER_URL
        + "/api/users",
}


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

@app.route(
    "/api/system",
    methods=["GET"]
)
def system_status():

    configured_services = (
        list_services()
        .get(
            "services",
            []
        )
    )

    services = []

    healthy_count = 0


    for service_name in configured_services:

        status = get_service_status(
            service_name
        )

        if (
            status.get("status")
            == "healthy"
        ):

            healthy_count += 1


        info = SERVICE_INFO.get(
            service_name,
            {}
        )


        services.append(
            {

                **status,

                "display_name":
                    info.get(
                        "display_name",
                        service_name
                    ),

                "short_name":
                    info.get(
                        "short_name",
                        service_name
                    ),

                "port":
                    info.get(
                        "port"
                    ),

                "technology":
                    info.get(
                        "technology",
                        ""
                    ),

                "database":
                    info.get(
                        "database",
                        ""
                    ),

                "description":
                    info.get(
                        "description",
                        ""
                    ),

                "mysql":
                    info.get(
                        "mysql",
                        False
                    ),
            }
        )


    total = len(
        services
    )

    incidents = (
        total
        - healthy_count
    )


    return jsonify(
        {

            "status":
                "healthy"
                if incidents == 0
                else "incident",

            "total": total,

            "healthy": healthy_count,

            "incidents": incidents,

            "services": services,

            "updated_at":
                datetime.now()
                .isoformat(),
        }
    )


# ============================================================
# START SERVICE
# ============================================================

@app.route(
    "/api/service/<service_name>/start",
    methods=["POST"]
)
def api_start_service(
    service_name
):

    return jsonify(
        start_service(
            service_name
        )
    )


# ============================================================
# STOP SERVICE
# ============================================================

@app.route(
    "/api/service/<service_name>/stop",
    methods=["POST"]
)
def api_stop_service(
    service_name
):

    return jsonify(
        stop_service(
            service_name
        )
    )


# ============================================================
# LOGS
# ============================================================

@app.route(
    "/api/service/<service_name>/logs",
    methods=["GET"]
)
def api_logs(
    service_name
):

    lines = request.args.get(
        "lines",
        100
    )


    return jsonify(
        get_service_logs(
            service_name,
            lines
        )
    )


# ============================================================
# DEPENDENCIES
# ============================================================

@app.route(
    "/api/service/<service_name>/dependencies",
    methods=["GET"]
)
def api_dependencies(
    service_name
):

    return jsonify(
        check_service_dependencies(
            service_name
        )
    )


# ============================================================
# MYSQL TEST
# ============================================================

@app.route(
    "/api/service/<service_name>/mysql",
    methods=["GET"]
)
def api_mysql(
    service_name
):

    return jsonify(
        check_mysql_database(
            service_name
        )
    )


# ============================================================
# SANITIZE DATA FOR UI
# ============================================================

def sanitize_value(
    value
):

    if isinstance(
        value,
        list
    ):

        return [
            sanitize_value(
                item
            )
            for item
            in value
        ]


    if isinstance(
        value,
        dict
    ):

        safe = {}


        blocked_fields = {
            "password",
            "token",
            "access_token",
            "refresh_token",
            "api_key",
            "apikey",
            "secret",
        }


        for key, item in value.items():

            if (
                str(key).lower()
                in blocked_fields
            ):

                continue


            safe[key] = sanitize_value(
                item
            )


        return safe


    return value


# ============================================================
# FETCH DATASET
# ============================================================

def fetch_dataset(
    dataset
):

    if dataset not in DATA_ENDPOINTS:

        return {
            "success": False,
            "error": "Unknown dataset.",
        }


    url = DATA_ENDPOINTS[
        dataset
    ]


    try:

        response = requests.get(
            url,
            timeout=5
        )


        response.raise_for_status()


        raw_data = response.json()


        safe_data = sanitize_value(
            raw_data
        )


        return {
            "success": True,
            "dataset": dataset,
            "data": safe_data,
        }


    except Exception as error:

        return {
            "success": False,
            "dataset": dataset,
            "error": str(
                error
            ),
        }


# ============================================================
# DATASET API
# ============================================================

@app.route(
    "/api/data/<dataset>",
    methods=["GET"]
)
def api_data(
    dataset
):

    result = fetch_dataset(
        dataset
    )


    status_code = (
        200
        if result.get(
            "success"
        )
        else 503
    )


    return jsonify(
        result
    ), status_code


# ============================================================
# DATA SUMMARY
# ============================================================

def extract_count(
    data
):

    if isinstance(
        data,
        list
    ):

        return len(
            data
        )


    if isinstance(
        data,
        dict
    ):

        keys = [

            "data",
            "items",
            "users",
            "bills",
            "predictions",
            "usage",
            "records",
        ]


        for key in keys:

            value = data.get(
                key
            )

            if isinstance(
                value,
                list
            ):

                return len(
                    value
                )


        if isinstance(
            data.get(
                "count"
            ),
            int
        ):

            return data[
                "count"
            ]


        return 1


    return 0


@app.route(
    "/api/data-summary",
    methods=["GET"]
)
def data_summary():

    output = {}


    for dataset in [

        "usage",
        "bills",
        "predictions",
        "users",

    ]:

        result = fetch_dataset(
            dataset
        )


        if result.get(
            "success"
        ):

            output[
                dataset
            ] = {

                "available": True,

                "count":
                    extract_count(
                        result.get(
                            "data"
                        )
                    ),
            }


        else:

            output[
                dataset
            ] = {

                "available": False,

                "count": 0,
            }


    return jsonify(
        output
    )


# ============================================================
# AI AGENT
# ============================================================

@app.route(
    "/api/agent",
    methods=["POST"]
)
def agent_request():

    data = request.get_json(
        silent=True
    ) or {}


    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()


    if not message:

        return jsonify(
            {
                "success": False,
                "error":
                    "Message is required."
            }
        ), 400


    try:

        response = run_sre_agent(
            message
        )


        return jsonify(
            {
                "success": True,
                "response": response,
            }
        )


    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(
                    error
                ),
            }
        ), 500


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "Smart Electricity AI SRE Showcase"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )