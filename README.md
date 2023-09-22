# Refactor Stats Maker

This is a simple CLI tool designed to generate progress statistics on bulk refactors.

This project relies on `ripgrep` as a replacement for `grep` and [Poetry](https://python-poetry.org/) for packaging and dependency management.

For the time being this CLI is custom built for [Web-Core-Client](https://gitlab.com/infraspeak/web/web-core-client) and a [specific refactor](https://infraspeak.gitlab.io/web/web-core-client/docs/guides/expands/how-to-refactor-old-expands.html) but can easily be turned into a more generic tool.

## Dependencies

* Python 3.11
* [Poetry](https://python-poetry.org/)
* [ripgrep](https://github.com/BurntSushi/ripgrep)

## How does it work

The source code for this project contains a hardcoded list of files in need of refactoring at the time the tool was first written.

> This means going back to this commit: `git checkout a4c5abe006^`

This list is matched against a search performed on the same repository at the present time.

The search pattern is also harcoded: `expanded: [',\\[].*`. This will remain untouched for the time being.

The difference is computed so we can tell which files have already been refactored so we mark those as completed and the other ones as to be done.

To determine to which fleet/team a given file is assigned to we perform match against the `CODEOWNERS` file of the repository.

## Simple example

Take note that this a deceptively simple example. Real world scenarios would include more than one file, created or modified tests, etc

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

Knowing which files are in need of refactors is useful from an individual contributor point of view but in a team effort a bit more structure would be nice.

That's where this tool comes in handy.

* Scans the target repository for files in need of refactor or already refactored
* Lists all matches grouped by team including completion percentage
* For each item it prints out it's status and src/ path
* A nice little ASCII bar chart at the end

> You can display the bar chart by itself by omitting the `-v` verbose flag

Let's see it in action:

```bash
refactor-stats-maker [YOUR_TARGET_REPOSITORY_DIR] -v
```

```
@infraspeak/buy-and-sell/bs1-asgard/frontend
  0.0% DONE (fixed 0 of 1 files)
  ❌ components/info/quote/components/summary/InfoQuoteSummary.store.ts
@infraspeak/cross-platform/cp1-kapteyn/frontend
  0.0% DONE (fixed 0 of 1 files)
  ❌ components/account/document/AccountDocument.store.ts
@infraspeak/cross-platform/cp2-stargate/frontend
  0.0% DONE (fixed 0 of 1 files)
  ❌ components/account/document/AccountDocument.store.ts
@infraspeak/maintenance-core/mc1-prometheus-finne-anni/frontend
  77.0% DONE (fixed 10 of 13 files)
  ✅ components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store.ts
  ✅ components/card/asset-housekeeper/CardAssetHousekeeper.store.ts
  ✅ components/info/asset/components/summary/InfoAssetSummary.store.ts
  ❌ components/info/failure/components/messages/InfoFailureMessages.store.ts
  ✅ components/info/failure/components/schedules/InfoFailureSchedules.store.ts
  ✅ components/info/failure/components/summary/InfoFailureSummary.store.ts
  ❌ components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts
  ✅ components/select/building/SelectBuilding.vue
  ✅ components/side-dialog/add-asset/SideDialogAddAsset.store.ts
  ❌ components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts
  ✅ components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts
  ✅ components/table/assets/TableAssets.store.ts
  ✅ models/failure/Failure.model.ts
@infraspeak/maintenance-core/mc2-starbug/frontend
  77.0% DONE (fixed 10 of 13 files)
  ✅ components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store.ts
  ✅ components/card/asset-housekeeper/CardAssetHousekeeper.store.ts
  ✅ components/info/asset/components/summary/InfoAssetSummary.store.ts
  ❌ components/info/failure/components/messages/InfoFailureMessages.store.ts
  ✅ components/info/failure/components/schedules/InfoFailureSchedules.store.ts
  ✅ components/info/failure/components/summary/InfoFailureSummary.store.ts
  ❌ components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts
  ✅ components/select/building/SelectBuilding.vue
  ✅ components/side-dialog/add-asset/SideDialogAddAsset.store.ts
  ❌ components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts
  ✅ components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts
  ✅ components/table/assets/TableAssets.store.ts
  ✅ models/failure/Failure.model.ts
Orphaned files
  0.0% DONE (fixed 0 of 8 files)
  ❌ components/account/general/AccountGeneral.store.ts
  ❌ components/account/notifications/AccountNotifications.store.ts
  ❌ components/account/settings/AccountSettings.store.ts
  ❌ components/select/warehouse/SelectWarehouse.vue
  ❌ components/side-dialog/cost-center/SideDialogCostCenter.store.ts
  ❌ components/side-dialog/other-cost/SideDialogOtherCost.store.ts
  ❌ components/side-dialog/utility-type/SideDialogUtilityType.store.ts
  ❌ views/utilities/ScreenUtilities.store.ts

────────────────────── Old expands refactor status % ──────────────────────
bs1-asgard 0/1                   0.0
cp1-kapteyn 0/1                  0.0
cp2-stargate 0/1                 0.0
mc1-prometheus-finne-anni 10/13 ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 77.0
mc2-starbug 10/13               ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 77.0
Orphaned files 0/8               0.0
```

Work can now more easily be distributed among fleet or teams and this report can be included in each MR to keep tabs on the progress made so far.

## Installation

Using pipx or pip install the latest `whl` file under `/dist`.

```bash
pipx install dist/refactor_stats_maker-0.1.1-py3-none-any.whl
```

The tool should now be globally available on your system.

## Development environment

Start a Poetry shell

`poetry shell`

### Running 

After performing your changes you can execute the tool in the Python virtual environment you've created previously.

```bash
poetry run python refactor-stats-maker [YOUR_TARGET_REPOSITORY_DIR] -v
```

### Building

```bash
poetry build
```

```
Building refactor-stats-maker (0.1.1)
  - Building sdist
  - Built refactor_stats_maker-0.1.1.tar.gz
  - Building wheel
  - Built refactor_stats_maker-0.1.1-py3-none-any.whl
```

> Check [Poetry's docs](https://python-poetry.org/docs/) for additional commands and flags
