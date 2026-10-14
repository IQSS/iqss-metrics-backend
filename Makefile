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
	test -f ./out/main_metrics.tsv || echo 'group   metric  title   value   unit    icon    color   url' > ./out/main_metrics.tsv

z_clean: ## ∟ clean artifacts metrics backend and link pre-requisites [private]
	rm -rfv iqss-metrics-dashboard
	rm -rfv out

z_deploy: ## ∟ Run deploy
	cd out && \
		git add -A -- . && \
		if git diff --cached --quiet; then \
			echo "No changes to data."; \
		else \
			git commit -m "Automated push of new data by iqss-metrics-backend on $(RUN_DATE)" && \
			git push origin master; \
		fi

z_run: ## ∟ Run backend
	pipenv run python main.py
