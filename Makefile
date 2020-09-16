build: z_build ## Run stat gathering script
run: z_run ## Run
clean: z_clean ## Clean

define log
 @echo "🔺 $(1)"
endef

z_build: ## ∟ build metrics backend and link pre-requisites [private]
	$(call log, Cloning IQSS/iqss-metrics-dashboard.git)
	git clone git@github.com:IQSS/iqss-metrics-dashboard.git
	ln -sf iqss-metrics-dashboard/assets/data out
	pyenv install -s
	pipenv install

z_clean: ## ∟ clean artifacts metrics backend and link pre-requisites [private]
	rm -rfv iqss-metrics-dashboard
	rm -rfv out

z_run: ## ∟ Run backend
	pipenv run python main.py
