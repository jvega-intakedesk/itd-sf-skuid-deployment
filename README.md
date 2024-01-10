# Salesforce Skuid Sync Script for Github Actions

It is a simple process since Skuid doesn't not involve a deployment. It will pull the production changes and push the local changes similar to what git pull/push would do.

The script expects a set of modules to be given to sync the modules. That happens becuase there is so much it can pull, push before giving an error with `skuid:page:pull: System.LimitException: JSON string exceeds heap size limit (System Code)`.

For the default logged entity, for the selected modules and no-modules, it will pull and push all changes.

## Inputs


|INPUT         |Optional|Type     |Default Value|Options|Description|
|--------------|:------:|:-------:|:-----------:|:-----:|:---------:|
|SF_AUTH_URL|N|string|-|-|The Salesforce Auth URL.|
|LOG_LEVEL|Y|option|error|trace, debug, info, warn, error, fatal|Skuid command flag `--loglevel`. Logging level for this command invocation. Defaults to Error.|
|TARGET_USERNAME_ALIAS|Y|string|-|-|Skuid command flag `--targetusername`. Username or alias for the target org; overrides default target org set with SF.|
|MODULES|Y|string|Intake_Modules, Old_Pages, Test-DEV, Verification_Modules|-|The Skuid command flag `--modules`. It will default to ITD modules. Should be passed separated by comma if more than one and spaces must be replaced by underscores.|

## Usage

To get the required SF_AUTH_URL, use the following command in your terminal.

```bash
sf org display --verbose --json -o <TARGET_ORG_ALIAS_OR_USERNAME>
```

On your GitHub action add as part of a step. Example:

```yml
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        uses: intakedesk/skuid-sync-action@v1.0
        with:
          SF_AUTH_URL: ${{ secrets.SF_AUTH_URL }}
```