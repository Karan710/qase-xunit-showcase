# Qase XUnit Showcase

This repository is a small .NET 8 xUnit example that demonstrates how to run automated tests and push the results into Qase TestOps in a clean, CI-friendly setup.

It is designed to show two things clearly:

- how a .NET test project is structured for GitHub Actions
- how Qase results can be uploaded from CI without checking secrets into source control

## What it does

The project runs a small xUnit suite against a fake login flow and a calculator:

- `UserCanLogin`
- `InvalidPassword_ShowsError`
- `ExperimentalFeature_NotYetTracked`
- `AdditionTest` parameterized theory cases

The tests are linked to Qase cases through the test metadata, and the build pipeline uploads the execution results to Qase after the suite runs.

If a test has no pre-mapped Qase case, the uploader creates one automatically from the test name so the run still gets recorded.

## How it does it

### 1. .NET test project

The app is a standard .NET 8 test project using xUnit.

```bash
dotnet restore
dotnet test
```

The test project is intentionally lightweight and does not depend on a local service or database. It behaves like a clean sample project that can be run locally or in CI.

### 2. GitHub Actions CI

The workflow in [.github/workflows/dotnet-tests.yml](.github/workflows/dotnet-tests.yml) does the following:

- installs the .NET SDK
- restores dependencies
- executes the test suite
- writes the TRX result file
- uploads the TRX as a workflow artifact
- posts the results to Qase using a custom Python script

This is triggered on pushes and pull requests.

### 3. Qase reporting flow

The repository uses a custom uploader in [scripts/upload_qase.py](scripts/upload_qase.py) to submit result data to the Qase API.

The script:

- reads the generated TRX file
- extracts each executed test result
- maps known tests to Qase case IDs
- creates a Qase case when needed
- creates a Qase test run
- submits each result to the Qase API using the result endpoint

The uploader is intentionally explicit about payloads so it is easier to debug API mismatches during CI.

### 4. Secret hygiene and repo safety

This repo keeps secrets out of source control.

The following are ignored:

- `qase.config.json`
- `bin/`
- `obj/`
- `TestResults/`
- generated build output and temporary artifacts

The project uses GitHub repository secrets such as:

- `QASE_TESTOPS_API_TOKEN`
- `QASE_TESTOPS_PROJECT`

The sample config file at `qase.config.sample.json` is a template only; it is not meant to contain real credentials.

## Local usage

```bash
dotnet restore
dotnet test
```

To run the uploader manually against a TRX file:

```bash
python3 scripts/upload_qase.py \
  --trx TestResults/test-results.trx \
  --project "$QASE_TESTOPS_PROJECT" \
  --token "$QASE_TESTOPS_API_TOKEN"
```

## Notes

This sample focuses on a working, minimal Qase integration pattern. It is intentionally kept simple so it can be used as a reference for:

- .NET 8 xUnit projects
- GitHub Actions test execution
- Qase TestOps result publishing
- secure secret handling in CI

The project is not meant to be a production app; it is a showcase and instructional setup for Qase-driven test reporting.
