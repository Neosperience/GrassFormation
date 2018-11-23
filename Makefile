project_name = GrassFormation
AWS_DEFAULT_REGION := $(if $(AWS_DEFAULT_REGION),$(AWS_DEFAULT_REGION),"us-east-1")
PUBLIC = true

src_dir = grassformation
dist_dir = dist
src_files = $(shell find $(src_dir) -type f -name '*.py')
s3_prefix = $(project_name)
stack_name = $(project_name)

dist_files = $(patsubst $(src_dir)/%.py,$(dist_dir)/%.py,$(src_files))
dist_req = $(dist_dir)/Pipenv

ifeq ($(PUBLIC), true)
	TEMPLATE_ACL=--acl public-read
endif

all: help

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
	@echo "    AWS_DEFAULT_REGION   : The AWS region of the deployment. Defaults to us-east-1."
	@echo "    SAM_S3_BUCKET        : The name of the deployment AWS bucket region. Required."
	@echo ""
	@echo "Global parameters can be set as shell environment variables or as command line arguments."
	@echo ""
	@echo "Examples:"
	@echo "    make local"
	@echo "    make deploy SAM_S3_BUCKET=my-bucket"
	@echo "    make remove"
	@echo ""

$(dist_dir):
	$(info [*] Creating $(dist_dir) folder)
	mkdir -p $(dist_dir)

$(dist_files): | $(dist_dir)

$(dist_req): Pipfile | $(dist_dir)
	$(info [+] Launching docker to install python requirements...)
	docker run -v $$PWD:/var/task \
		-it lambci/lambda:build-python3.6 /bin/bash \
		-c 'make _package SAM_S3_BUCKET=$(SAM_S3_BUCKET) AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION)'

.PHONY: _package
_package:
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

$(dist_dir)/.$(SAM_S3_BUCKET):
ifeq ($(SAM_S3_BUCKET),)
$(error SAM_S3_BUCKET variable is not set. Set it as environment variable or as command line argument.)
endif
	@echo ""
	@if aws s3 ls "s3://$(SAM_S3_BUCKET)" 2>&1 | grep -q 'NoSuchBucket'; then \
		@echo "[*] Creating s3 bucket $(SAM_S3_BUCKET)..." \
		aws s3 mb s3://$(SAM_S3_BUCKET) --region $(AWS_DEFAULT_REGION); \
	else; \
		@echo "[+] S3 bucket $(SAM_S3_BUCKET) already exists." \
	fi;
	@touch $@

packaged-template.yaml: sam-template.yaml $(dist_dir)/.dist | $(dist_dir)/.$(SAM_S3_BUCKET)
	@echo "[+] Packing and uploading distribution package..."
	aws cloudformation package \
		--template-file sam-template.yaml \
		--output-template-file packaged-template.yaml \
		--s3-bucket $(SAM_S3_BUCKET) \
		--s3-prefix $(s3_prefix)
	@echo "[*] Distribution package uploaded to s3://$(SAM_S3_BUCKET)/$(s3_prefix)/ folder"
	@if [ $(PUBLIC) == "true" ]; then \
		export PACKAGE_KEY=`sed -n 's/^[[:space:]]*S3Key: //p' packaged-template.yaml | head -1`; \
		echo "[+] Setting public read access on s3:/$(SAM_S3_BUCKET)/$$PACKAGE_KEY ..."; \
		aws s3api put-object-acl --bucket $(SAM_S3_BUCKET) --key $$PACKAGE_KEY $(TEMPLATE_ACL); \
	fi;
	@echo "[+] Uploading the packaged CloudFormation template..."
	aws s3 cp packaged-template.yaml s3://$(SAM_S3_BUCKET)/$(s3_prefix)/template.yaml $(TEMPLATE_ACL)
	@echo "[*] CloudFormation template uploaded to s3://$(SAM_S3_BUCKET)/$(s3_prefix)/template.yaml"

#:    deploy           : Deploys or updates the service with CloudFormation
.PHONY: deploy
deploy: $(dist_dir)/.deploy

$(dist_dir)/.deploy: packaged-template.yaml
	$(info [+] Deploying the service...)
	aws cloudformation deploy \
		--template-file packaged-template.yaml \
		--stack-name $(stack_name) \
		--capabilities CAPABILITY_IAM \
		--region $(AWS_DEFAULT_REGION)
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
