let systemState = null;

let agentBusy = false;



// ============================================================
// BASIC HELPERS
// ============================================================

function escapeHtml(value) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );
}



// ============================================================
// SYSTEM REFRESH
// ============================================================

async function refreshSystem() {

    try {

        const response = await fetch(
            "/api/system"
        );


        const data = await response.json();


        systemState = data;


        renderSystem(
            data
        );

    }

    catch (error) {

        console.error(
            error
        );

    }

}



// ============================================================
// RENDER SYSTEM
// ============================================================

function renderSystem(data) {

    const badge = document.getElementById(
        "systemBadge"
    );


    const serviceCount = document.getElementById(
        "serviceCount"
    );


    const healthyCount = document.getElementById(
        "healthyCount"
    );


    const incidentCount = document.getElementById(
        "incidentCount"
    );


    serviceCount.textContent =
        data.total;


    healthyCount.textContent =
        data.healthy;


    incidentCount.textContent =
        data.problems;


    if (
        data.status === "healthy"
    ) {

        badge.className =
            "system-badge healthy";

        badge.innerHTML =
            `
            <span class="status-dot"></span>
            All systems operational
            `;

    }

    else {

        badge.className =
            "system-badge incident";

        badge.innerHTML =
            `
            <span class="status-dot"></span>
            ${data.problems} incident${data.problems === 1 ? "" : "s"}
            `;

    }


    const lastUpdated = document.getElementById(
        "lastUpdated"
    );


    lastUpdated.textContent =
        "Updated "
        + new Date().toLocaleTimeString();


    renderServices(
        data.services
    );

}



// ============================================================
// RENDER SERVICE CARDS
// ============================================================

function renderServices(services) {

    const grid = document.getElementById(
        "servicesGrid"
    );


    grid.innerHTML = "";


    services.forEach(
        service => {

            const healthy =
                service.status === "healthy";


            const card = document.createElement(
                "article"
            );


            card.className =
                "service-card";


            let latency = "—";


            if (
                service.response_time_ms !== undefined
            ) {

                latency =
                    Number(
                        service.response_time_ms
                    ).toFixed(
                        1
                    );

            }


            card.innerHTML =
                `

                <div class="service-top">

                    <div class="service-name">
                        ${escapeHtml(service.title)}
                    </div>

                    <div
                        class="service-state ${healthy ? "healthy" : "problem"}"
                    >

                        <span class="dot"></span>

                        ${escapeHtml(service.status)}

                    </div>

                </div>


                <div class="service-description">
                    ${escapeHtml(service.description)}
                </div>


                <div class="service-stat">

                    <div class="service-latency">

                        ${latency}

                        <small>
                            ${latency === "—" ? "" : "ms"}
                        </small>

                    </div>


                    <div class="service-port">
                        PORT ${service.port}
                    </div>

                </div>


                <div class="service-actions">

                    <button
                        onclick="viewLogs(
                            '${service.service}'
                        )"
                    >
                        Logs
                    </button>


                    <button
                        onclick="viewDependencies(
                            '${service.service}'
                        )"
                    >
                        Dependencies
                    </button>


                    ${
                        !healthy
                        ?
                        `
                        <button
                            class="recover-button"
                            onclick="recoverService(
                                '${service.service}'
                            )"
                        >
                            Recover
                        </button>
                        `
                        :
                        ""
                    }

                </div>
                `;


            grid.appendChild(
                card
            );

        }
    );

}



// ============================================================
// DATA SUMMARY
// ============================================================

async function refreshDataSummary() {

    try {

        const response = await fetch(
            "/api/data-summary"
        );


        const data = await response.json();


        setCount(
            "usageCount",
            data.meter_readings
        );


        setCount(
            "billCount",
            data.bills
        );


        setCount(
            "predictionCount",
            data.predictions
        );


        setCount(
            "userCount",
            data.users
        );

    }

    catch (error) {

        console.error(
            error
        );

    }

}



function setCount(
    elementId,
    item
) {

    const element = document.getElementById(
        elementId
    );


    if (
        item
        &&
        item.available
    ) {

        element.textContent =
            item.count;

    }

    else {

        element.textContent =
            "—";

    }

}



// ============================================================
// AI AGENT
// ============================================================

async function sendAgentMessage(
    suppliedMessage = null
) {

    if (
        agentBusy
    ) {

        return;

    }


    const input = document.getElementById(
        "agentInput"
    );


    let message =
        suppliedMessage
        ||
        input.value.trim();


    if (
        !message
    ) {

        return;

    }


    input.value = "";


    const output = document.getElementById(
        "agentOutput"
    );


    const sendButton = document.getElementById(
        "sendButton"
    );


    agentBusy = true;


    sendButton.disabled = true;


    output.innerHTML =
        `

        <div class="agent-loading">

            <div class="loader"></div>

            <div>

                Agent is investigating the live system...

            </div>

        </div>
        `;


    try {

        const response = await fetch(
            "/api/agent",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(
                    {
                        message: message
                    }
                )

            }
        );


        const data = await response.json();


        if (
            data.success
        ) {

            output.textContent =
                data.response;

        }

        else {

            output.textContent =
                "Agent error:\n"
                +
                data.error;

        }


        await refreshSystem();

        await refreshDataSummary();

    }

    catch (error) {

        output.textContent =
            "Unable to contact the AI SRE agent.\n\n"
            +
            error;

    }

    finally {

        agentBusy = false;

        sendButton.disabled = false;

    }

}



// ============================================================
// QUICK PROMPTS
// ============================================================

function askQuickPrompt(
    message
) {

    sendAgentMessage(
        message
    );

}



function runFullInvestigation() {

    sendAgentMessage(

        "Investigate the whole Smart Electricity System. "
        +
        "Find any incidents, analyze logs and dependencies, "
        +
        "and automatically recover stopped services when safe. "
        +
        "Verify the final system status."

    );

}



// ============================================================
// LOG VIEWER
// ============================================================

async function viewLogs(
    serviceName
) {

    openModal(
        serviceName + " · Logs",
        "Loading..."
    );


    try {

        const response = await fetch(

            `/api/service/${serviceName}/logs?lines=80`

        );


        const data = await response.json();


        const content =
            data.logs
            ||
            JSON.stringify(
                data,
                null,
                2
            );


        setModalContent(
            content
        );

    }

    catch (error) {

        setModalContent(
            String(
                error
            )
        );

    }

}



// ============================================================
// DEPENDENCIES
// ============================================================

async function viewDependencies(
    serviceName
) {

    openModal(
        serviceName
        +
        " · Dependencies",
        "Loading..."
    );


    try {

        const response = await fetch(

            `/api/service/${serviceName}/dependencies`

        );


        const data = await response.json();


        setModalContent(

            JSON.stringify(
                data,
                null,
                2
            )

        );

    }

    catch (error) {

        setModalContent(
            String(
                error
            )
        );

    }

}



// ============================================================
// CONTROLLED RECOVERY
// ============================================================

async function recoverService(
    serviceName
) {

    openModal(
        serviceName
        +
        " · Recovery",
        "Starting controlled recovery..."
    );


    try {

        const response = await fetch(

            `/api/service/${serviceName}/recover`,

            {
                method: "POST"
            }

        );


        const data = await response.json();


        setModalContent(

            JSON.stringify(
                data,
                null,
                2
            )

        );


        await refreshSystem();

    }

    catch (error) {

        setModalContent(
            String(
                error
            )
        );

    }

}



// ============================================================
// MODAL
// ============================================================

function openModal(
    title,
    content
) {

    document.getElementById(
        "modalTitle"
    ).textContent =
        title;


    document.getElementById(
        "modalContent"
    ).textContent =
        content;


    document.getElementById(
        "modal"
    ).classList.remove(
        "hidden"
    );

}



function setModalContent(
    content
) {

    document.getElementById(
        "modalContent"
    ).textContent =
        content;

}



function closeModal() {

    document.getElementById(
        "modal"
    ).classList.add(
        "hidden"
    );

}



// ============================================================
// EVENTS
// ============================================================

document.getElementById(
    "refreshButton"
).addEventListener(
    "click",
    async () => {

        await refreshSystem();

        await refreshDataSummary();

    }
);



document.getElementById(
    "agentInput"
).addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter"
            &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendAgentMessage();

        }

    }
);



document.querySelector(
    ".modal-backdrop"
).addEventListener(
    "click",
    closeModal
);



// ============================================================
// START
// ============================================================

async function initializeDashboard() {

    await refreshSystem();

    await refreshDataSummary();


    setInterval(
        refreshSystem,
        8000
    );


    setInterval(
        refreshDataSummary,
        15000
    );

}



initializeDashboard();