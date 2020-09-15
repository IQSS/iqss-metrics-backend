build: z_build ## Run R hello world.
clean: z_clean ## Clean

define log
 @echo "🔺 $(1)"
endef

z_build: ## ∟ build metrics backend and link pre-requisites [private]
	$(call log, Cloning IQSS/iqss-metrics-dashboard.git)
	git clone git@github.com:IQSS/iqss-metrics-dashboard.git
	ln -sf iqss-metrics-dashboard/assets/data out

z_clean:
	rm -rfv iqss-metrics-dashboard
	rm -rfv out
