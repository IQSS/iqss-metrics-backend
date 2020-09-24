build: z_build ## Run stat gathering script
run: z_run ## Run
clean: z_clean ## Clean
deploy: z_deploy ## Deploy

define log
 @echo "🔺 $(1)"
endef

RUN_DATE=$(shell date)

z_build: ## ∟ build metrics backend and link pre-requisites [private]
	$(call log, Cloning IQSS/iqss-metrics-dashboard.git)
	git clone git@github.com:IQSS/iqss-metrics-dashboard.git
	ln -sf iqss-metrics-dashboard/assets/data out
	pipenv install

z_clean: ## ∟ clean artifacts metrics backend and link pre-requisites [private]
	rm -rfv iqss-metrics-dashboard
	rm -rfv out

z_deploy:
  cd out && \
    git add -A && \
    git commit -a -m "Automated push of new data by iqss-metrics-backend on $(RUN_DATE)" && \
    git push origin master
z_run: ## ∟ Run backend
	pipenv run python main.py
