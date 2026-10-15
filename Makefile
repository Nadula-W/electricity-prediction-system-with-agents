ROOT := E:/CeyTech Labs/electricity prediction system with agents

.PHONY: start meter billing prediction user agent health


# ============================================================
# START ALL 4 SERVICES
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
	@echo ============================================================
	@echo All 4 services have been launched.
	@echo ============================================================
	@echo.
	@echo Logs will be stored inside:
	@echo $(ROOT)/logs
	@echo.


# ============================================================
# METER DATA SERVICE
# ============================================================

meter:
	@echo Starting Meter Data Service...
	@cmd /c start "Meter Data Service - 3000" /D "$(ROOT)" cmd /k "python scripts/run_service.py meter"


# ============================================================
# BILLING SERVICE
# ============================================================

billing:
	@echo Starting Billing Service...
	@cmd /c start "Billing Service - 3001" /D "$(ROOT)" cmd /k "python scripts/run_service.py billing"


# ============================================================
# PREDICTION SERVICE
# ============================================================

prediction:
	@echo Starting Prediction Service...
	@cmd /c start "Prediction Service - 3002" /D "$(ROOT)" cmd /k "python scripts/run_service.py prediction"


# ============================================================
# USER SERVICE
# ============================================================

user:
	@echo Starting User Service...
	@cmd /c start "User Service - 8081" /D "$(ROOT)" cmd /k "python scripts/run_service.py user"


# ============================================================
# RUN AI SRE AGENT
# ============================================================

agent:
	@python main.py
	

# ============================================================
# SAME AS AGENT
# ============================================================

health:
	@python main.py