# Qase XUnit Showcase

This repository is a minimal .NET 8 test project using xUnit and GitHub Actions.
It is intentionally kept free of secrets and runtime-generated files so it can be
opened, built, and tested cleanly in CI.

## Requirements

- .NET 8 SDK

## Run locally

```bash
dotnet restore
dotnet test
```

## GitHub Actions

The project includes a workflow at `.github/workflows/dotnet-tests.yml` that runs
on pushes and pull requests.

## Secret handling

The repository ignores local secret files such as `qase.config.json` and uses
GitHub repository secrets for any future CI integrations. A sample config is
provided at `qase.config.sample.json`, but it is not committed with real values.

## Notes

This repo has been simplified so that the test suite runs reliably in GitHub and
in normal local CI environments without the Qase reporter breaking xUnit test
execution.

## Known issue: `[Tags]` and package versioning

This project originally pinned `Qase.XUnit.Reporter` to `1.1.1`, which pulls
in a `Qase.Csharp.Commons` version that **predates the `[Tags]` attribute**
shown in Qase's own docs — using it fails to compile with `CS0246`. The
`.csproj` now uses a floating version (`Version="*"`) so `dotnet restore`
picks up the latest release instead.

The floating version also means `Metadata.Comment(...)` (shown in Qase's
docs under "Comments") didn't resolve in this build's resolved package
version, so it's removed from `UserCanLogin` here rather than left broken.

**To check exactly what version you actually built against:**
```bash
dotnet list package
```
Cross-reference that against the [Qase.Csharp.Commons NuGet
page](https://www.nuget.org/packages/Qase.Csharp.Commons) and the
[usage.md](https://github.com/qase-tms/qase-csharp/blob/main/Qase.XUnit.Reporter/docs/usage.md)
docs for that specific version before re-adding `[Tags(...)]` or
`Metadata.Comment(...)` — floating `*` can pick up a different version on a
future `dotnet restore` (e.g. after a new release ships), so what compiles
today isn't guaranteed to stay identical without pinning to a fixed version
once you know which one actually has the features you want.

## What each test demonstrates

- **`UserCanLogin`** — linked to an existing Qase case via `[QaseIds(123)]`,
  custom title, custom field, and step tracking (`[Qase]` + `[Step]`
  methods). Passes.
- **`InvalidPassword_ShowsError`** — deliberately fails, so once uploaded
  you'll see one passed and one failed result in the same run.
- **`ExperimentalFeature_NotYetTracked`** — has `[Ignore]`, so it executes
  locally but its result is **not** sent to Qase at all (different from
  xUnit's own `Skip`, which *does* get reported, as "Skipped").
- **`AdditionTest`** — a `[Theory]` with three `[InlineData]` rows; Qase
  reports each parameter set as its own separate result under case 300.

## Test cases without `[QaseIds]`

If you omit `[QaseIds]` (as this project doesn't for any test, but worth
knowing), the reporter auto-creates a case in Qase based on the test's name
and file path, and matches the same case on subsequent runs as long as
those don't change.

## Relationship to Abhijeet's setup

This project is what a working reporter-based setup looks like when the
target framework supports it. It's useful as a reference for:
- Confirming the config file shape/keys are correct when troubleshooting
  someone else's `qase.config.json`
- Any other customer/project on .NET 6+ asking "how do I use the XUnit
  reporter"

It does **not** apply directly to Abhijeet's case, since his project is on
.NET Framework 4.x — for that, use the NUnit custom-upload sample instead.
