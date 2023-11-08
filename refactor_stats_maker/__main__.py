import sys
from pathlib import Path
from typing import List

from codeowners import CodeOwners
from ripgrepy import Ripgrepy

import repository_helpers
import stats_helpers

# BASELINE for STATS
team_assignement_baselines = {
    "@infraspeak/buy-and-sell/bs1-asgard/frontend": [
        "components/side-dialog/email/sale/SideDialogEmailSale.store.ts",
        "components/info/purchase/components/documents/InfoPurchaseDocuments.store.ts",
        "components/info/purchase/components/summary/InfoPurchaseSummary.store.ts",
        "components/info/sale/components/summary/InfoSaleSummary.store.ts",
        "components/info/quote/components/items/InfoQuoteItems.store.ts",
        "components/info/quote/components/summary/InfoQuoteSummary.store.ts",
        "components/info/client/custom-sale-prices/InfoClientCustomSalePrices.store.ts",
        "components/side-dialog/email/quote/SideDialogEmailQuote.store.ts",
        "components/history/quote/HistoryQuote.store.ts",
        "components/history/sale/HistorySale.store.ts",
    ],
    "@infraspeak/cross-platform/cp1-kapteyn/frontend": [
        "components/account/document/AccountDocument.store.ts"
    ],
    "@infraspeak/cross-platform/cp2-stargate/frontend": [
        "components/account/document/AccountDocument.store.ts"
    ],
    "@infraspeak/maintenance-core/mc1-prometheus-finne-anni/frontend": [
        "views/dashboard/components/widget-device-location"
        "/ScreenDashboardWidgetDeviceLocation.vue",
        "views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts",
        "components/side-dialog/select-asset/SideDialogSelectAsset.store.ts",
        "models/failure-element/FailureElement.model.ts",
        "models/failure/Failure.model.ts",
        "components/info/asset/components/costs/InfoAssetCosts.store.ts",
        "components/info/failure/components/schedules/InfoFailureSchedules.store.ts",
        "components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts",
        "components/info/failure/components/messages/InfoFailureMessages.store.ts",
        "components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis"
        ".store.ts",
        "components/info/asset/components/characteristics/InfoAssetCharacteristics"
        ".store.ts",
        "components/info/failure/components/requests/InfoFailureRequests.store.ts",
        "components/info/asset/components/summary/InfoAssetSummary.store.ts",
        "components/info/asset/components/planned/InfoAssetPlanned.store.ts",
        "components/info/failure/components/attachments/InfoFailureAttachments.store"
        ".ts",
        "components/info/failure/components/costs/InfoFailureCosts.store.ts",
        "components/info/failure/components/stats/InfoFailureStats.store.ts",
        "components/info/failure/components/summary/InfoFailureSummary.store.ts",
        "components/info/scheduled-work/components/attachments"
        "/InfoScheduledWorkAttachments.store.ts",
        "components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store"
        ".ts",
        "components/info/scheduled-work/components/requests/InfoScheduledWorkRequests"
        ".store.ts",
        "components/info/scheduled-work/components/gatekeeper"
        "/InfoScheduledWorkGatekeeper.store.ts",
        "components/info/scheduled-work/components/summary/InfoScheduledWorkSummary"
        ".store.ts",
        "components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store"
        ".ts",
        "components/info/scheduled-work/components/failures/InfoScheduledWorkFailures"
        ".store.ts",
        "components/info/scheduled-work/components/planner-activity"
        "/InfoScheduledWorkPlannerActivity.store.ts",
        "components/history/asset/HistoryAsset.store.ts",
        "components/history/scheduled-work/HistoryScheduledWork.store.ts",
        "components/history/failure/HistoryFailure.vue",
        "components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist"
        ".store.ts",
        "components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store"
        ".ts",
        "components/side-dialog/select-intervention/SideDialogSelectIntervention"
        ".store.ts",
        "components/side-dialog/report-failure/SideDialogReportFailure.store.ts",
        "components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts",
        "components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter"
        ".store.ts",
        "components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics"
        ".store.ts",
        "components/side-dialog/add-asset/SideDialogAddAsset.store.ts",
        "components/card/element-scheduled-work-task/CardElementScheduledWorkTask"
        ".store.ts",
        "components/card/asset-housekeeper/CardAssetHousekeeper.store.ts",
        "components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store"
        ".ts",
        "components/table/assets/TableAssets.store.ts",
        "components/select/building/SelectBuilding.vue",
    ],
    "@infraspeak/maintenance-core/mc2-starbug/frontend": [
        "views/dashboard/components/widget-device-location"
        "/ScreenDashboardWidgetDeviceLocation.vue",
        "views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts",
        "components/side-dialog/select-asset/SideDialogSelectAsset.store.ts",
        "models/failure-element/FailureElement.model.ts",
        "models/failure/Failure.model.ts",
        "components/info/asset/components/costs/InfoAssetCosts.store.ts",
        "components/info/failure/components/schedules/InfoFailureSchedules.store.ts",
        "components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts",
        "components/info/failure/components/messages/InfoFailureMessages.store.ts",
        "components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis"
        ".store.ts",
        "components/info/asset/components/characteristics/InfoAssetCharacteristics"
        ".store.ts",
        "components/info/failure/components/requests/InfoFailureRequests.store.ts",
        "components/info/asset/components/summary/InfoAssetSummary.store.ts",
        "components/info/asset/components/planned/InfoAssetPlanned.store.ts",
        "components/info/failure/components/attachments/InfoFailureAttachments.store"
        ".ts",
        "components/info/failure/components/costs/InfoFailureCosts.store.ts",
        "components/info/failure/components/stats/InfoFailureStats.store.ts",
        "components/info/failure/components/summary/InfoFailureSummary.store.ts",
        "components/info/scheduled-work/components/attachments"
        "/InfoScheduledWorkAttachments.store.ts",
        "components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store"
        ".ts",
        "components/info/scheduled-work/components/requests/InfoScheduledWorkRequests"
        ".store.ts",
        "components/info/scheduled-work/components/gatekeeper"
        "/InfoScheduledWorkGatekeeper.store.ts",
        "components/info/scheduled-work/components/summary/InfoScheduledWorkSummary"
        ".store.ts",
        "components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store"
        ".ts",
        "components/info/scheduled-work/components/failures/InfoScheduledWorkFailures"
        ".store.ts",
        "components/info/scheduled-work/components/planner-activity"
        "/InfoScheduledWorkPlannerActivity.store.ts",
        "components/history/asset/HistoryAsset.store.ts",
        "components/history/scheduled-work/HistoryScheduledWork.store.ts",
        "components/history/failure/HistoryFailure.vue",
        "components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist"
        ".store.ts",
        "components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store"
        ".ts",
        "components/side-dialog/select-intervention/SideDialogSelectIntervention"
        ".store.ts",
        "components/side-dialog/report-failure/SideDialogReportFailure.store.ts",
        "components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts",
        "components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter"
        ".store.ts",
        "components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics"
        ".store.ts",
        "components/side-dialog/add-asset/SideDialogAddAsset.store.ts",
        "components/card/element-scheduled-work-task/CardElementScheduledWorkTask"
        ".store.ts",
        "components/card/asset-housekeeper/CardAssetHousekeeper.store.ts",
        "components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store"
        ".ts",
        "components/table/assets/TableAssets.store.ts",
        "components/select/building/SelectBuilding.vue",
    ],
    "@pedromcosta": ["store/root/Root.store.ts"],
    "Orphaned files": [
        "views/utilities/ScreenUtilities.store.ts",
        "components/side-dialog/other-cost/SideDialogOtherCost.store.ts",
        "components/side-dialog/utility-type/SideDialogUtilityType.store.ts",
        "components/side-dialog/material/SideDialogMaterial.store.ts",
        "components/side-dialog/cost-center/SideDialogCostCenter.store.ts",
        "components/account/settings/AccountSettings.store.ts",
        "components/account/notifications/AccountNotifications.store.ts",
        "components/account/general/AccountGeneral.store.ts",
        "components/select/warehouse/SelectWarehouse.vue",
    ],
}


def get_files_to_refactor(
        repo_path: str, regex: str, exclude: List[str] = []
) -> List[str]:
    src_path = str(Path(f"{repo_path}/src").expanduser())

    rg = Ripgrepy(regex, src_path)

    # SEE https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md#manual-filtering
    # -globs
    excluded_extensions_glob = ", ".join(exclude)
    excluded_extensions_glob = f"!*.{{{excluded_extensions_glob}}}"

    files_to_refactor = (
        rg.glob(excluded_extensions_glob).files_with_matches().run().as_string
    )

    lines = files_to_refactor.split("\n")

    return [f.replace(src_path + "/", "") for f in lines if f != ""]


def get_codeowners(repo_path) -> CodeOwners:
    # PARSE CODEOWNERS FILE
    codeowners_file = Path(f"{repo_path}/CODEOWNERS").expanduser()
    codeowners = None

    try:
        with codeowners_file.open() as f:
            codeowners = CodeOwners(f.read())
            return codeowners
    except IOError:
        print(
            f"Cannot find a CODEOWNERS file "
            f"are you sure WebCoreClient is located in {repo_path}"
        )
        exit(1)


def get_team_assignments(files: List[str], codeowners: CodeOwners):
    # ASSIGN EACH FILE TO A TEAM

    team_assignments = {}

    for file_to_refactor in files:
        teams = codeowners.of("src/" + file_to_refactor)
        teams = [t[1] for t in teams]
        if not teams:
            teams = ["Orphaned files"]
        for team in teams:
            assigned_files = team_assignments.get(team, [])
            team_assignments[team] = assigned_files + [file_to_refactor]

    return team_assignments


def run():
    repo_path = None
    verbose = False
    copy_to_clipboard = False
    format_for_gitlab = False
    args = []

    match sys.argv:
        case [_]:
            print("Empty repository path")
            exit(1)
        case [_, path]:
            repo_path = path
        case [_, path, *args]:
            repo_path = path
            args = args

    verbose = "-v" in args
    copy_to_clipboard = "--copy" in args
    format_for_gitlab = "--gitlab" in args

    # VALIDATE THE REPOSITORY PATH
    if repo_path is None:
        print("Invalid repository path")
        exit(1)

    # LOOK FOR FILES TO REFACTOR

    # We're ignoring test files because they are most likely testing API calls
    # whenever a 'expanded: ' match is found
    file_paths = get_files_to_refactor(repo_path, "expanded: [',\\[].*", ["spec.ts"])
    codeowners = get_codeowners(repo_path)

    team_assignments = get_team_assignments(file_paths, codeowners)

    stats_helpers.display_team_assignments(
        team_assignments,
        team_assignement_baselines,
        verbose,
        format_for_gitlab,
        copy_to_clipboard,
    )


def get_team_assignment_baseline(repo_dir, commit_hash, regex, codeowners):
    working_dir = repository_helpers.clone_repo_at_baseline(commit_hash)
    files = get_files_to_refactor(working_dir, regex)
    team_assignment_baseline = get_team_assignments(files, codeowners)
    return team_assignment_baseline


if __name__ == "__main__":
    # run()
    repo_path = "~/repo/web/web-core-client"
    commit_hash = "83dfde9d4bde87b2c14597873e1ccc1eaf8e034d"
    regex = "import IsButton"
    current_files = get_files_to_refactor(repo_path, regex)
    codeowners = get_codeowners(repo_path)
    team_assignment = get_team_assignments(current_files, codeowners)
    team_assignement_baseline = get_team_assignment_baseline(
        repo_path, commit_hash, regex, codeowners
    )

    print("BASELINE: ")
    print("##############")
    print(team_assignement_baseline)
    print("##############")
    print("##############")
    print(team_assignment)
    print("##############")

    stats_helpers.display_team_assignments(
        team_assignment, team_assignement_baseline, True
    )
