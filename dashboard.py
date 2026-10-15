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

from agent.tools import (
    list_services,
    get_service_status,
    get_service_logs,
    check_service_dependencies,
    check_mysql_database,
)

from agent.actions import (
    start_service,
)

from agent.sre_agent import (
    run_sre_agent,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder="showcase/templates",
    static_folder="showcase/static",
)


# ============================================================
# SERVICE DISPLAY INFORMATION
# ============================================================

SERVICE_INFO = {

    "meter-data-service": {
        "title": "Meter Data",
        "port": 3000,
        "description": "Electricity usage readings",
    },

    "billing-service": {
        "title": "Billing",
        "port": 3001,
        "description": "Electricity billing engine",
    },

    "prediction-service": {
        "title": "Prediction",
        "port": 3002,
        "description": "Consumption forecasting",
    },

    "user-service": {
        "title": "User Service",
        "port": 8081,
        "description": "Customer and user management",
    },
}


# ============================================================
# SERVICE URLS
# ============================================================

METER_SERVICE_URL = os.getenv(
    "METER_SERVICE_URL",
    "http://localhost:3000",
)

BILLING_SERVICE_URL = os.getenv(
    "BILLING_SERVICE_URL",
    "http://localhost:3001",
)

PREDICTION_SERVICE_URL = os.getenv(
    "PREDICTION_SERVICE_URL",
    "http://localhost:3002",
)

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://localhost:8081",
)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# SYSTEM STATUS API
# ============================================================

@app.route(
    "/api/system",
    methods=["GET"]
)
def system_status():

    service_names = list_services().get(
        "services",
        []
    )

    results = []

    healthy_count = 0


    for service_name in service_names:

        status = get_service_status(
            service_name
        )

        if status.get("status") == "healthy":

            healthy_count += 1


        display = SERVICE_INFO.get(
            service_name,
            {}
        )


        results.append(
            {
                **status,

                "title": display.get(
                    "title",
                    service_name
                ),

                "description": display.get(
                    "description",
                    ""
                ),

                "port": display.get(
                    "port"
                ),
            }
        )


    total_services = len(
        results
    )


    problem_count = (
        total_services
        - healthy_count
    )


    if problem_count == 0:

        overall_status = "healthy"

    else:

        overall_status = "incident"


    return jsonify(
        {
            "status": overall_status,

            "healthy": healthy_count,

            "problems": problem_count,

            "total": total_services,

            "services": results,

            "updated_at": datetime.now().isoformat(),
        }
    )


# ============================================================
# AI AGENT API
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
                "error": "Message is required.",
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
# SERVICE LOG API
# ============================================================

@app.route(
    "/api/service/<service_name>/logs",
    methods=["GET"]
)
def service_logs(
    service_name
):

    lines = request.args.get(
        "lines",
        60
    )


    result = get_service_logs(
        service_name,
        lines
    )


    return jsonify(
        result
    )


# ============================================================
# SERVICE DEPENDENCY API
# ============================================================

@app.route(
    "/api/service/<service_name>/dependencies",
    methods=["GET"]
)
def service_dependencies(
    service_name
):

    result = check_service_dependencies(
        service_name
    )


    return jsonify(
        result
    )


# ============================================================
# MYSQL CHECK API
# ============================================================

@app.route(
    "/api/service/<service_name>/mysql",
    methods=["GET"]
)
def service_mysql(
    service_name
):

    result = check_mysql_database(
        service_name
    )


    return jsonify(
        result
    )


# ============================================================
# CONTROLLED SERVICE RECOVERY
# ============================================================

@app.route(
    "/api/service/<service_name>/recover",
    methods=["POST"]
)
def recover_service(
    service_name
):

    result = start_service(
        service_name
    )


    return jsonify(
        result
    )


# ============================================================
# HELPER
# FETCH DATA FROM MICROSERVICE
# ============================================================

def fetch_json(
    url
):

    try:

        response = requests.get(
            url,
            timeout=3
        )


        if response.status_code != 200:

            return {
                "available": False,
                "count": 0,
            }


        data = response.json()


        if isinstance(
            data,
            list
        ):

            count = len(
                data
            )


        elif isinstance(
            data,
            dict
        ):

            count = None


            possible_lists = [

                "data",
                "items",
                "users",
                "bills",
                "predictions",
                "usage",
                "records",
            ]


            for key in possible_lists:

                value = data.get(
                    key
                )

                if isinstance(
                    value,
                    list
                ):

                    count = len(
                        value
                    )

                    break


            if count is None:

                count = data.get(
                    "count",
                    1
                )


        else:

            count = 0


        return {
            "available": True,
            "count": count,
        }


    except Exception:

        return {
            "available": False,
            "count": 0,
        }


# ============================================================
# DEMO DATA SUMMARY
# ============================================================

@app.route(
    "/api/data-summary",
    methods=["GET"]
)
def data_summary():

    usage = fetch_json(
        (
            METER_SERVICE_URL
            + "/api/usage"
        )
    )


    bills = fetch_json(
        (
            BILLING_SERVICE_URL
            + "/api/bills"
        )
    )


    predictions = fetch_json(
        (
            PREDICTION_SERVICE_URL
            + "/api/predictions"
        )
    )


    users = fetch_json(
        (
            USER_SERVICE_URL
            + "/api/users"
        )
    )


    return jsonify(
        {
            "meter_readings": usage,

            "bills": bills,

            "predictions": predictions,

            "users": users,
        }
    )


# ============================================================
# RUN DASHBOARD
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=" * 60
    )

    print(
        "AI SRE Command Center"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Dashboard:"
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