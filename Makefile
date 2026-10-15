ROOT := E:/CeyTech Labs/electricity prediction system with agents/sources/smart-electricity-system

.PHONY: start meter billing prediction user agent


# ============================================================
# START ALL SERVICES
# ============================================================

start:
	@echo ============================================================
	@echo Starting Smart Electricity System
	@echo ============================================================
	@$(MAKE) meter
	@$(MAKE) billing
	@$(MAKE) prediction
	@$(MAKE) user
	@echo.
	@echo All four services have been launched.
	@echo.
	@echo Meter Data : http://localhost:3000
	@echo Billing    : http://localhost:3001
	@echo Prediction : http://localhost:3002
	@echo User       : http://localhost:8081


# ============================================================
# METER DATA SERVICE - PORT 3000
# ============================================================

meter:
	@echo Starting Meter Data Service...
	@cmd /c start "Meter Data Service - 3000" /D "$(ROOT)/meter-data-service" cmd /k "node server.js"


# ============================================================
# BILLING SERVICE - PORT 3001
# ============================================================

billing:
	@echo Starting Billing Service...
	@cmd /c start "Billing Service - 3001" /D "$(ROOT)/billing-service" cmd /k "node app.js"


# ============================================================
# PREDICTION SERVICE - PORT 3002
# ============================================================

prediction:
	@echo Starting Prediction Service...
	@cmd /c start "Prediction Service - 3002" /D "$(ROOT)/prediciton-service/prediction-service" cmd /k "node app.js"


# ============================================================
# USER SERVICE - PORT 8081
# ============================================================

user:
	@echo Starting User Service...
	@cmd /c start "User Service - 8081" /D "$(ROOT)/user-service" cmd /k "mvn spring-boot:run"


# ============================================================
# RUN PYTHON AI SRE AGENT
# ============================================================

agent:
	@echo Starting AI SRE Incident Agent...
	@python main.py