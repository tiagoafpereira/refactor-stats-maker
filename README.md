# Refactor Stats Maker

This is a simple CLI tool designed to generate progress statistics on bulk refactors.

This project relies on `ripgrep` as a replacement for `grep` and [Poetry](https://python-poetry.org/) for packaging and
dependency management.

For the time being this CLI is custom built for [Web-Core-Client](https://gitlab.com/infraspeak/web/web-core-client) and
a [specific refactor](https://infraspeak.gitlab.io/web/web-core-client/docs/guides/expands/how-to-refactor-old-expands.html)
but can easily be turned into a more generic tool.

## Dependencies

* Python 3.11
* [Poetry](https://python-poetry.org/)
* [ripgrep](https://github.com/BurntSushi/ripgrep)

## How does it work

The source code for this project contains a hardcoded list of files in need of refactoring at the time the tool was
first written.

> This means going back to this commit: `git checkout a4c5abe006^`

This list is matched against a search performed on the same repository at the present time.

The search pattern is also harcoded: `expanded: [',\\[].*`. This will remain untouched for the time being.

The difference is computed so we can tell which files have already been refactored so we mark those as completed and the
other ones as to be done.

To determine to which fleet/team a given file is assigned to we perform match against the `CODEOWNERS` file of the
repository.

## Simple example

Take note that this a deceptively simple example. Real world scenarios would include more than one file, created or
modified tests, etc

Let's say we have a number of files where we want to perform the following refactor:

This

```typescript
expanded: 'fizz'
```

becomes this

```typescript
expand: {
    fizz: {}
}
```

Using `ripgrep` we can scan a repository for files in need of refactor.

```bash
rg "expanded: '.*" --files-with-matches
```

```bash
src/views/utilities/ScreenUtilities.store.ts
src/views/management/gatekeeper/ScreenManagementGatekeeper.spec.ts
docs/guides/expands/how-to-refactor-old-expands.md
src/components/modal/scheduled-work/ModalScheduledWork.spec.ts
src/components/info/failure/components/messages/InfoFailureMessages.store.ts
src/components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts
src/components/info/quote/components/summary/InfoQuoteSummary.store.ts
src/components/info/quote/components/items/components/table/components/row/InfoQuoteItemsTableRow.spec.ts
src/components/info/quote/components/items/components/table/components/row-card/InfoQuoteItemsTableRowCard.spec.ts
src/components/account/general/AccountGeneral.store.ts
src/components/account/document/AccountDocument.store.ts
src/components/account/settings/AccountSettings.store.ts
src/components/account/notifications/AccountNotifications.store.ts
src/components/side-dialog/other-cost/SideDialogOtherCost.store.ts
src/components/side-dialog/utility-type/SideDialogUtilityType.store.ts
src/components/side-dialog/cost-center/SideDialogCostCenter.store.ts
src/components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts
src/components/select/warehouse/SelectWarehouse.vue
```

We know now which files have one or more usages that we want to refactor.

## Usage

Knowing which files are in need of refactors is useful from an individual contributor point of view but in a team effort
a bit more structure would be nice.

That's where this tool comes in handy.

* Scans the target repository for files in need of refactor or already refactored
* Lists all matches grouped by team including completion percentage
* For each item it prints out it's status and src/ path
* A nice little ASCII bar chart at the end

> You can display the bar chart by itself by omitting the `--list` option

Let's see it in action:

```bash
refactor-stats-maker [YOUR_TARGET_REPOSITORY_DIR] --type expands --list
```

```
──────────────────── OVERALL REFACTORING STATUS OF OLD EXPANDS 59.68% ────────────────────
Orphaned files 6/9              ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 66.67
bs1-asgard 5/10                 ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 50.0
cp1-kapteyn 1/1                 ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 100.0
cp2-stargate 1/1                ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 100.0
mc1-prometheus-finne-anni 24/41 ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 58.54
mc2-starbug 24/41               ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 58.54
store 1/1                       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 100.0

Orphaned files 66.67% DONE (fixed 6 of 9 files)
  ✅ components/account/general/AccountGeneral.store.ts
  ✅ components/account/notifications/AccountNotifications.store.ts
  ✅ components/account/settings/AccountSettings.store.ts
  ✅ components/select/warehouse/SelectWarehouse.vue
  ✅ components/side-dialog/cost-center/SideDialogCostCenter.store.ts
  ❌ components/side-dialog/material/SideDialogMaterial.store.ts
  ❌ components/side-dialog/other-cost/SideDialogOtherCost.store.ts
  ✅ components/side-dialog/utility-type/SideDialogUtilityType.store.ts
  ❌ views/utilities/ScreenUtilities.store.ts
bs1-asgard 50.0% DONE (fixed 5 of 10 files)
  ✅ components/history/quote/HistoryQuote.store.ts
  ✅ components/history/sale/HistorySale.store.ts
  ❌ components/info/client/custom-sale-prices/InfoClientCustomSalePrices.store.ts
  ❌ components/info/purchase/components/documents/InfoPurchaseDocuments.store.ts
  ✅ components/info/purchase/components/summary/InfoPurchaseSummary.store.ts
  ❌ components/info/quote/components/items/InfoQuoteItems.store.ts
  ❌ components/info/quote/components/summary/InfoQuoteSummary.store.ts
  ❌ components/info/sale/components/summary/InfoSaleSummary.store.ts
  ✅ components/side-dialog/email/quote/SideDialogEmailQuote.store.ts
  ✅ components/side-dialog/email/sale/SideDialogEmailSale.store.ts
cp1-kapteyn 100.0% DONE (fixed 1 of 1 files)
  ✅ components/account/document/AccountDocument.store.ts
cp2-stargate 100.0% DONE (fixed 1 of 1 files)
  ✅ components/account/document/AccountDocument.store.ts
mc1-prometheus-finne-anni 58.54% DONE (fixed 24 of 41 files)
  ✅ components/card/asset-housekeeper/CardAssetHousekeeper.store.ts
  ✅ components/card/element-scheduled-work-task/CardElementScheduledWorkTask.store.ts
  ❌ components/history/asset/HistoryAsset.store.ts
  ❌ components/history/failure/HistoryFailure.vue
  ❌ components/history/scheduled-work/HistoryScheduledWork.store.ts
  ✅ components/info/asset/components/characteristics/InfoAssetCharacteristics.store.ts
  ❌ components/info/asset/components/costs/InfoAssetCosts.store.ts
  ❌ components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis.store.ts
  ✅ components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts
  ❌ components/info/asset/components/planned/InfoAssetPlanned.store.ts
  ✅ components/info/asset/components/summary/InfoAssetSummary.store.ts
  ❌ components/info/failure/components/attachments/InfoFailureAttachments.store.ts
  ❌ components/info/failure/components/costs/InfoFailureCosts.store.ts
  ✅ components/info/failure/components/messages/InfoFailureMessages.store.ts
  ❌ components/info/failure/components/requests/InfoFailureRequests.store.ts
  ✅ components/info/failure/components/schedules/InfoFailureSchedules.store.ts
  ❌ components/info/failure/components/stats/InfoFailureStats.store.ts
  ✅ components/info/failure/components/summary/InfoFailureSummary.store.ts
  ✅ components/info/scheduled-work/components/attachments/InfoScheduledWorkAttachments.store.ts
  ✅ components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store.ts
  ❌ components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store.ts
  ❌ components/info/scheduled-work/components/failures/InfoScheduledWorkFailures.store.ts
  ✅ components/info/scheduled-work/components/gatekeeper/InfoScheduledWorkGatekeeper.store.ts
  ❌ components/info/scheduled-work/components/planner-activity/InfoScheduledWorkPlannerActivity.store.ts
  ❌ components/info/scheduled-work/components/requests/InfoScheduledWorkRequests.store.ts
  ✅ components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts
  ❌ components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store.ts
  ✅ components/select/building/SelectBuilding.vue
  ✅ components/side-dialog/add-asset/SideDialogAddAsset.store.ts
  ✅ components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics.store.ts
  ✅ components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts
  ✅ components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts
  ✅ components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist.store.ts
  ✅ components/side-dialog/report-failure/SideDialogReportFailure.store.ts
  ✅ components/side-dialog/select-asset/SideDialogSelectAsset.store.ts
  ✅ components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts
  ✅ components/table/assets/TableAssets.store.ts
  ❌ models/failure-element/FailureElement.model.ts
  ✅ models/failure/Failure.model.ts
  ✅ views/dashboard/components/widget-device-location/ScreenDashboardWidgetDeviceLocation.vue
  ❌ views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts
mc2-starbug 58.54% DONE (fixed 24 of 41 files)
  ✅ components/card/asset-housekeeper/CardAssetHousekeeper.store.ts
  ✅ components/card/element-scheduled-work-task/CardElementScheduledWorkTask.store.ts
  ❌ components/history/asset/HistoryAsset.store.ts
  ❌ components/history/failure/HistoryFailure.vue
  ❌ components/history/scheduled-work/HistoryScheduledWork.store.ts
  ✅ components/info/asset/components/characteristics/InfoAssetCharacteristics.store.ts
  ❌ components/info/asset/components/costs/InfoAssetCosts.store.ts
  ❌ components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis.store.ts
  ✅ components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts
  ❌ components/info/asset/components/planned/InfoAssetPlanned.store.ts
  ✅ components/info/asset/components/summary/InfoAssetSummary.store.ts
  ❌ components/info/failure/components/attachments/InfoFailureAttachments.store.ts
  ❌ components/info/failure/components/costs/InfoFailureCosts.store.ts
  ✅ components/info/failure/components/messages/InfoFailureMessages.store.ts
  ❌ components/info/failure/components/requests/InfoFailureRequests.store.ts
  ✅ components/info/failure/components/schedules/InfoFailureSchedules.store.ts
  ❌ components/info/failure/components/stats/InfoFailureStats.store.ts
  ✅ components/info/failure/components/summary/InfoFailureSummary.store.ts
  ✅ components/info/scheduled-work/components/attachments/InfoScheduledWorkAttachments.store.ts
  ✅ components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store.ts
  ❌ components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store.ts
  ❌ components/info/scheduled-work/components/failures/InfoScheduledWorkFailures.store.ts
  ✅ components/info/scheduled-work/components/gatekeeper/InfoScheduledWorkGatekeeper.store.ts
  ❌ components/info/scheduled-work/components/planner-activity/InfoScheduledWorkPlannerActivity.store.ts
  ❌ components/info/scheduled-work/components/requests/InfoScheduledWorkRequests.store.ts
  ✅ components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts
  ❌ components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store.ts
  ✅ components/select/building/SelectBuilding.vue
  ✅ components/side-dialog/add-asset/SideDialogAddAsset.store.ts
  ✅ components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics.store.ts
  ✅ components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts
  ✅ components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts
  ✅ components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist.store.ts
  ✅ components/side-dialog/report-failure/SideDialogReportFailure.store.ts
  ✅ components/side-dialog/select-asset/SideDialogSelectAsset.store.ts
  ✅ components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts
  ✅ components/table/assets/TableAssets.store.ts
  ❌ models/failure-element/FailureElement.model.ts
  ✅ models/failure/Failure.model.ts
  ✅ views/dashboard/components/widget-device-location/ScreenDashboardWidgetDeviceLocation.vue
  ❌ views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts
store 100.0% DONE (fixed 1 of 1 files)
  ✅ store/root/Root.store.ts
```

Work can now more easily be distributed among fleet or teams and this report can be included in each MR to keep tabs on
the progress made so far.

## Installation

Using pipx or pip install the latest `whl` file under `/dist`.

```bash
pipx install dist/refactor_stats_maker-0.4.1-py3-none-any.whl
```

The tool should now be globally available on your system.

To check all available options use the `--help` flag:

```commandline
$ poetry run python -m refactor-stats-maker --help
Usage: python -m refactor-stats-maker [OPTIONS] REPOSITORY_PATH

Options:
  --version                       Show the version and exit.
  -l, --list                      Display file list.
  -c, --copy                      Copy output to clipboard.
  -g, --gitlab                    Format output in GitLab flavored Markdown.
  -t, --type [expands|class-based]
                                  Type of statistics to generate.
  --help                          Show this message and exit.
```

## Development environment

Start a Poetry shell

`poetry shell`

### Running

After performing your changes you can execute the tool in the Python virtual environment you've created previously.

```bash
poetry run python -m refactor_stats_maker [YOUR_TARGET_REPOSITORY_DIR] --type expands
```

### Building

```bash
poetry build
```

```
Building refactor-stats-maker (0.4.1)
  - Building sdist
  - Built refactor_stats_maker-0.4.1.tar.gz
  - Building wheel
  - Built refactor_stats_maker-0.4.1-py3-none-any.whl
```

> Check [Poetry's docs](https://python-poetry.org/docs/) for additional commands and flags
