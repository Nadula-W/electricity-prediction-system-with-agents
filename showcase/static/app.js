let agentBusy = false;


// ============================================================
// HTML ESCAPE
// ============================================================

function escapeHtml(value) {

    return String(
        value ?? ""
    )

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
// NORMALIZE API DATA
// ============================================================

function normalizeRows(
    data
) {

    if (
        Array.isArray(
            data
        )
    ) {

        return data;
    }


    if (
        data
        &&
        typeof data === "object"
    ) {

        const possibleKeys = [

            "data",
            "items",
            "users",
            "bills",
            "predictions",
            "usage",
            "records",
        ];


        for (
            const key
            of possibleKeys
        ) {

            if (
                Array.isArray(
                    data[key]
                )
            ) {

                return data[
                    key
                ];
            }
        }


        return [
            data
        ];
    }


    return [];
}


// ============================================================
// SYSTEM
// ============================================================

async function loadSystem() {

    try {

        const response =
            await fetch(
                "/api/system"
            );


        const data =
            await response.json();


        renderSummary(
            data
        );


        renderServices(
            data.services
        );

    }

    catch (error) {

        console.error(
            error
        );
    }
}


// ============================================================
// SUMMARY
// ============================================================

function renderSummary(
    data
) {

    document.getElementById(
        "totalServices"
    ).textContent =
        data.total;


    document.getElementById(
        "healthyServices"
    ).textContent =
        data.healthy;


    document.getElementById(
        "incidentServices"
    ).textContent =
        data.incidents;


    const status =
        document.getElementById(
            "systemStatus"
        );


    if (
        data.incidents === 0
    ) {

        status.className =
            "system-status healthy";


        status.textContent =
            `${data.healthy}/${data.total} Healthy`;

    }

    else {

        status.className =
            "system-status incident";


        status.textContent =
            `${data.incidents} Incident${data.incidents === 1 ? "" : "s"}`;
    }
}


// ============================================================
// SERVICE CARDS
// ============================================================

function renderServices(
    services
) {

    const grid =
        document.getElementById(
            "servicesGrid"
        );


    grid.innerHTML =
        "";


    services.forEach(
        service => {

            const healthy =
                service.status
                ===
                "healthy";


            const responseTime =
                service.response_time_ms
                !== undefined
                ?
                `${service.response_time_ms} ms`
                :
                "—";


            const card =
                document.createElement(
                    "article"
                );


            card.className =
                "service-card";


            let databaseButton =
                "";


            if (
                service.mysql
            ) {

                databaseButton =
                    `
                    <button
                        onclick="checkDatabase(
                            '${service.service}'
                        )"
                    >
                        DB Test
                    </button>
                    `;
            }


            let powerButton =
                "";


            if (
                healthy
            ) {

                powerButton =
                    `
                    <button
                        class="stop-button"
                        onclick="stopService(
                            '${service.service}'
                        )"
                    >
                        Stop Service
                    </button>
                    `;

            }

            else {

                powerButton =
                    `
                    <button
                        class="start-button"
                        onclick="startService(
                            '${service.service}'
                        )"
                    >
                        Start Service
                    </button>
                    `;
            }


            card.innerHTML =
                `

                <div class="service-top">

                    <div>

                        <h3 class="service-title">

                            ${escapeHtml(
                                service.display_name
                            )}

                        </h3>


                        <div class="service-description">

                            ${escapeHtml(
                                service.description
                            )}

                        </div>

                    </div>


                    <div
                        class="
                            service-status
                            ${healthy ? "healthy" : "problem"}
                        "
                    >

                        <i></i>

                        ${escapeHtml(
                            service.status
                        )}

                    </div>

                </div>


                <div class="service-meta">

                    <div class="meta-item">

                        <label>
                            Technology
                        </label>

                        <strong>
                            ${escapeHtml(
                                service.technology
                            )}
                        </strong>

                    </div>


                    <div class="meta-item">

                        <label>
                            Database
                        </label>

                        <strong>
                            ${escapeHtml(
                                service.database
                            )}
                        </strong>

                    </div>


                    <div class="meta-item">

                        <label>
                            Port / Response
                        </label>

                        <strong>
                            ${service.port}
                            ·
                            ${responseTime}
                        </strong>

                    </div>

                </div>


                <div class="service-actions">

                    <button
                        onclick="showLogs(
                            '${service.service}'
                        )"
                    >
                        Logs
                    </button>


                    <button
                        onclick="showDependencies(
                            '${service.service}'
                        )"
                    >
                        Dependencies
                    </button>


                    ${databaseButton}

                    ${powerButton}

                </div>
                `;


            grid.appendChild(
                card
            );
        }
    );
}


// ============================================================
// STOP SERVICE
// ============================================================

async function stopService(
    service
) {

    const confirmed =
        confirm(
            `Stop ${service}?\n\n`
            +
            "This is useful for demonstrating "
            +
            "AI automatic recovery."
        );


    if (
        !confirmed
    ) {

        return;
    }


    openModal(
        "Stopping Service",
        `Stopping ${service}...`
    );


    try {

        const response =
            await fetch(
                `/api/service/${service}/stop`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        setModalContent(
            JSON.stringify(
                data,
                null,
                2
            )
        );


        await loadSystem();

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
// START SERVICE
// ============================================================

async function startService(
    service
) {

    openModal(
        "Starting Service",
        `Starting ${service}...`
    );


    try {

        const response =
            await fetch(
                `/api/service/${service}/start`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        setModalContent(
            JSON.stringify(
                data,
                null,
                2
            )
        );


        await loadSystem();

        await loadAllData();

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
// LOGS
// ============================================================

async function showLogs(
    service
) {

    openModal(
        service
        +
        " · Logs",
        "Loading logs..."
    );


    try {

        const response =
            await fetch(
                `/api/service/${service}/logs?lines=100`
            );


        const data =
            await response.json();


        setModalContent(
            data.logs
            ||
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
// DEPENDENCIES
// ============================================================

async function showDependencies(
    service
) {

    openModal(
        service
        +
        " · Dependencies",
        "Checking dependencies..."
    );


    try {

        const response =
            await fetch(
                `/api/service/${service}/dependencies`
            );


        const data =
            await response.json();


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
// DATABASE TEST
// ============================================================

async function checkDatabase(
    service
) {

    openModal(
        service
        +
        " · MySQL Verification",
        "Testing database connection..."
    );


    try {

        const response =
            await fetch(
                `/api/service/${service}/mysql`
            );


        const data =
            await response.json();


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
// LOAD ALL DATA
// ============================================================

async function loadAllData() {

    await Promise.all(

        [

            loadDataset(
                "bills",
                "billsTable",
                "billCount"
            ),

            loadDataset(
                "predictions",
                "predictionsTable",
                "predictionCount"
            ),

            loadDataset(
                "usage",
                "usageTable",
                "usageCount"
            ),

            loadDataset(
                "users",
                "usersTable",
                "userCount"
            ),

        ]

    );
}


// ============================================================
// LOAD ONE DATASET
// ============================================================

async function loadDataset(
    dataset,
    containerId,
    countId
) {

    const container =
        document.getElementById(
            containerId
        );


    const count =
        document.getElementById(
            countId
        );


    container.innerHTML =
        '<div class="empty-message">Loading...</div>';


    try {

        const response =
            await fetch(
                `/api/data/${dataset}`
            );


        const result =
            await response.json();


        if (
            !result.success
        ) {

            container.innerHTML =
                `
                <div class="empty-message">
                    Service unavailable
                </div>
                `;

            count.textContent =
                "—";

            return;
        }


        const rows =
            normalizeRows(
                result.data
            );


        count.textContent =
            rows.length;


        renderMiniTable(
            rows,
            container
        );

    }

    catch (error) {

        container.innerHTML =
            `
            <div class="empty-message">
                Unable to load data
            </div>
            `;

        count.textContent =
            "—";
    }
}


// ============================================================
// TABLE
// ============================================================

function renderMiniTable(
    rows,
    container
) {

    if (
        rows.length === 0
    ) {

        container.innerHTML =
            `
            <div class="empty-message">
                No records available.
            </div>
            `;

        return;
    }


    const keys =
        Object.keys(
            rows[0]
        );


    let html =
        "<table><thead><tr>";


    keys.forEach(
        key => {

            html +=
                `<th>
                    ${escapeHtml(key)}
                </th>`;
        }
    );


    html +=
        "</tr></thead><tbody>";


    rows.forEach(
        row => {

            html +=
                "<tr>";


            keys.forEach(
                key => {

                    let value =
                        row[key];


                    if (
                        typeof value
                        ===
                        "object"
                        &&
                        value !== null
                    ) {

                        value =
                            JSON.stringify(
                                value
                            );
                    }


                    html +=
                        `<td title="${escapeHtml(value)}">
                            ${escapeHtml(value)}
                        </td>`;
                }
            );


            html +=
                "</tr>";
        }
    );


    html +=
        "</tbody></table>";


    container.innerHTML =
        html;
}


// ============================================================
// AI AGENT
// ============================================================

async function runAgent(
    message
) {

    if (
        agentBusy
    ) {

        return;
    }


    agentBusy =
        true;


    const output =
        document.getElementById(
            "agentOutput"
        );


    output.textContent =
        "AI SRE Agent is investigating the live system...";


    try {

        const response =
            await fetch(
                "/api/agent",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                message: message
                            }
                        )
                }
            );


        const data =
            await response.json();


        output.textContent =
            data.success
            ?
            data.response
            :
            "Agent Error:\n"
            +
            data.error;


        await loadSystem();

        await loadAllData();

    }

    catch (error) {

        output.textContent =
            "Unable to contact agent.\n\n"
            +
            error;
    }

    finally {

        agentBusy =
            false;
    }
}


// ============================================================
// SEND CUSTOM MESSAGE
// ============================================================

function sendAgent() {

    const input =
        document.getElementById(
            "agentInput"
        );


    const message =
        input.value.trim();


    if (
        !message
    ) {

        return;
    }


    input.value =
        "";


    runAgent(
        message
    );
}


document.getElementById(
    "agentInput"
).addEventListener(
    "keydown",
    event => {

        if (
            event.key
            ===
            "Enter"
        ) {

            event.preventDefault();

            sendAgent();
        }
    }
);


// ============================================================
// SCROLL AGENT
// ============================================================

function scrollToAgent() {

    document.getElementById(
        "agentSection"
    ).scrollIntoView(
        {
            behavior: "smooth"
        }
    );
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
// INITIALIZE
// ============================================================

async function initialize() {

    await loadSystem();

    await loadAllData();


    setInterval(
        loadSystem,
        5000
    );


    setInterval(
        loadAllData,
        15000
    );
}


initialize();