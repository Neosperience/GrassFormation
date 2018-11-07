project_name = GrassFormation
region = us-east-1
s3_bucket = sam-packages.neosperience.com

src_dir = grassformation
dist_dir = dist
src_files = $(shell find $(src_dir) -type f -name '*.py')
s3_prefix = $(project_name)
stack_name = $(project_name)

dist_files = $(patsubst $(src_dir)/%.py,$(dist_dir)/%.py,$(src_files))
dist_req = $(dist_dir)/Pipenv

all: deploy

#:    help             : Prints this help
.PHONY: help
help: Makefile
	@echo ""
	@echo "Use make tool to convenientely deploy and manage this serverless service."
	@echo ""
	@echo "Available commands:"
	@sed -n 's/^#://p' $<
	@echo ""
	@echo "Global parameters:"
	@echo "    region           : The AWS region of the deployment. Defaults to us-east-1."
	@echo "    s3_bucket        : The name of the deployment AWS bucket region. Defaults to sam-packages.neosperience.com."
	@echo ""
	@echo "Examples:"
	@echo "    make local"
	@echo "    make deploy region=us-west-1"
	@echo "    make remove"
	@echo ""

$(dist_dir):
	$(info [*] Creating $(dist_dir) folder)
	mkdir -p $(dist_dir)

$(dist_files): | $(dist_dir)

$(dist_req): Pipfile | $(dist_dir)
	$(info [+] Launching docker to install python requirements...)
	docker run -v $$PWD:/var/task -it lambci/lambda:build-python3.6 /bin/bash -c 'make _package'

.PHONY: _package
_package:
	$(info [+] Installing python requirements...)
	pip install pipenv
	pipenv lock -r > requirements.txt
	pipenv run pip install \
		--isolated \
		--disable-pip-version-check \
		-Ur requirements.txt -t $(dist_dir)
	$(info [*] Cleaning eventual cache files)
	find $(dist_dir) -name '*~' -exec rm -f {} +
	find $(dist_dir) -name '__pycache__' -exec rm -rf {} +
	rm -f requirements.txt
	cp Pipfile $(dist_req)

$(dist_dir)/%.py: $(src_dir)/%.py
	mkdir -p $(dir $@)
	cp $< $@

$(dist_dir)/.dist: $(dist_req) $(dist_files)
	@touch $@

.PHONY: clean
clean:
	$(info [*] Cleaning $(dist_dir) folder)
	rm -rf $(dist_dir) || true

#:    local            : Local testing of the API. Needs sam cli to be installed.
.PHONY: local
local:
	$(info [+] Starting local test environment...)
	sam local start-api

$(dist_dir)/.bucket:
	@echo ""
	@echo "Creating s3 bucket..."
	aws s3 mb s3://$(s3_bucket)
	@touch $@

packaged-template.yaml: sam-template.yaml $(dist_dir)/.dist | $(dist_dir)/.bucket
	$(info [+] Packing and uploading distribution package...)
	aws cloudformation package \
		--template-file sam-template.yaml \
		--output-template-file packaged-template.yaml \
		--s3-bucket $(s3_bucket) \
		--s3-prefix $(s3_prefix)

#:    deploy           : Deploys or updates the service with CloudFormation
.PHONY: deploy
deploy: $(dist_dir)/.deploy

$(dist_dir)/.deploy: packaged-template.yaml
	$(info [+] Deploying the service...)
	aws cloudformation deploy \
		--template-file packaged-template.yaml \
		--stack-name $(stack_name) \
		--capabilities CAPABILITY_IAM \
		--region $(region)
	@touch $@
	$(info [*] Stack outputs:)
	@aws cloudformation describe-stacks \
	    --stack-name $(stack_name) \
	    --query 'Stacks[].Outputs'

#:    remove           : Removes the deployed service with CloudFormation
.PHONY: remove
remove:
	$(info [+] Removing the service...)
	aws cloudformation delete-stack \
		--stack-name $(stack_name)
	@rm -f $(dist_dir)/.deploy || true
