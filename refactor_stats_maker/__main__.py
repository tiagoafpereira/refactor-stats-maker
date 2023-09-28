from pathlib import Path
from codeowners import CodeOwners
from ripgrepy import Ripgrepy
import sys
import re
import plotext as plt
import pyperclip

# BASELINE for STATS
team_baselines = {
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
        "components/history/sale/HistorySale.store.ts"
    ],
    "@infraspeak/cross-platform/cp1-kapteyn/frontend": [
        "components/account/document/AccountDocument.store.ts"
    ],
    "@infraspeak/cross-platform/cp2-stargate/frontend": [
        "components/account/document/AccountDocument.store.ts"
    ],
    "@infraspeak/maintenance-core/mc1-prometheus-finne-anni/frontend": [
        "views/dashboard/components/widget-device-location/ScreenDashboardWidgetDeviceLocation.vue",
        "views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts",
        "components/side-dialog/select-asset/SideDialogSelectAsset.store.ts",
        "models/failure-element/FailureElement.model.ts",
        "models/failure/Failure.model.ts",
        "components/info/asset/components/costs/InfoAssetCosts.store.ts",
        "components/info/failure/components/schedules/InfoFailureSchedules.store.ts",
        "components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts",
        "components/info/failure/components/messages/InfoFailureMessages.store.ts",
        "components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis.store.ts",
        "components/info/asset/components/characteristics/InfoAssetCharacteristics.store.ts",
        "components/info/failure/components/requests/InfoFailureRequests.store.ts",
        "components/info/asset/components/summary/InfoAssetSummary.store.ts",
        "components/info/asset/components/planned/InfoAssetPlanned.store.ts",
        "components/info/failure/components/attachments/InfoFailureAttachments.store.ts",
        "components/info/failure/components/costs/InfoFailureCosts.store.ts",
        "components/info/failure/components/stats/InfoFailureStats.store.ts",
        "components/info/failure/components/summary/InfoFailureSummary.store.ts",
        "components/info/scheduled-work/components/attachments/InfoScheduledWorkAttachments.store.ts",
        "components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store.ts",
        "components/info/scheduled-work/components/requests/InfoScheduledWorkRequests.store.ts",
        "components/info/scheduled-work/components/gatekeeper/InfoScheduledWorkGatekeeper.store.ts",
        "components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts",
        "components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store.ts",
        "components/info/scheduled-work/components/failures/InfoScheduledWorkFailures.store.ts",
        "components/info/scheduled-work/components/planner-activity/InfoScheduledWorkPlannerActivity.store.ts",
        "components/history/asset/HistoryAsset.store.ts",
        "components/history/scheduled-work/HistoryScheduledWork.store.ts",
        "components/history/failure/HistoryFailure.vue",
        "components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist.store.ts",
        "components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store.ts",
        "components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts",
        "components/side-dialog/report-failure/SideDialogReportFailure.store.ts",
        "components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts",
        "components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts",
        "components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics.store.ts",
        "components/side-dialog/add-asset/SideDialogAddAsset.store.ts",
        "components/card/element-scheduled-work-task/CardElementScheduledWorkTask.store.ts",
        "components/card/asset-housekeeper/CardAssetHousekeeper.store.ts",
        "components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store.ts",
        "components/table/assets/TableAssets.store.ts",
        "components/select/building/SelectBuilding.vue"
    ],
    "@infraspeak/maintenance-core/mc2-starbug/frontend": [
        "views/dashboard/components/widget-device-location/ScreenDashboardWidgetDeviceLocation.vue",
        "views/housekeeper/components/dashboard/ScreenHousekeeperDashboard.store.ts",
        "components/side-dialog/select-asset/SideDialogSelectAsset.store.ts",
        "models/failure-element/FailureElement.model.ts",
        "models/failure/Failure.model.ts",
        "components/info/asset/components/costs/InfoAssetCosts.store.ts",
        "components/info/failure/components/schedules/InfoFailureSchedules.store.ts",
        "components/info/asset/components/open-failures/InfoAssetOpenFailures.store.ts",
        "components/info/failure/components/messages/InfoFailureMessages.store.ts",
        "components/info/asset/components/economic-analysis/InfoAssetEconomicAnalysis.store.ts",
        "components/info/asset/components/characteristics/InfoAssetCharacteristics.store.ts",
        "components/info/failure/components/requests/InfoFailureRequests.store.ts",
        "components/info/asset/components/summary/InfoAssetSummary.store.ts",
        "components/info/asset/components/planned/InfoAssetPlanned.store.ts",
        "components/info/failure/components/attachments/InfoFailureAttachments.store.ts",
        "components/info/failure/components/costs/InfoFailureCosts.store.ts",
        "components/info/failure/components/stats/InfoFailureStats.store.ts",
        "components/info/failure/components/summary/InfoFailureSummary.store.ts",
        "components/info/scheduled-work/components/attachments/InfoScheduledWorkAttachments.store.ts",
        "components/info/scheduled-work/components/costs/InfoScheduledWorkCosts.store.ts",
        "components/info/scheduled-work/components/requests/InfoScheduledWorkRequests.store.ts",
        "components/info/scheduled-work/components/gatekeeper/InfoScheduledWorkGatekeeper.store.ts",
        "components/info/scheduled-work/components/summary/InfoScheduledWorkSummary.store.ts",
        "components/info/scheduled-work/components/audit/InfoScheduledWorkAudit.store.ts",
        "components/info/scheduled-work/components/failures/InfoScheduledWorkFailures.store.ts",
        "components/info/scheduled-work/components/planner-activity/InfoScheduledWorkPlannerActivity.store.ts",
        "components/history/asset/HistoryAsset.store.ts",
        "components/history/scheduled-work/HistoryScheduledWork.store.ts",
        "components/history/failure/HistoryFailure.vue",
        "components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist.store.ts",
        "components/info/scheduled-work/components/tasks/InfoScheduledWorkTasks.store.ts",
        "components/side-dialog/select-intervention/SideDialogSelectIntervention.store.ts",
        "components/side-dialog/report-failure/SideDialogReportFailure.store.ts",
        "components/side-dialog/failure-asset/SideDialogFailureAsset.store.ts",
        "components/side-dialog/building-utility-meter/SideDialogBuildingUtilityMeter.store.ts",
        "components/side-dialog/asset-characteristics/SideDialogAssetCharacteristics.store.ts",
        "components/side-dialog/add-asset/SideDialogAddAsset.store.ts",
        "components/card/element-scheduled-work-task/CardElementScheduledWorkTask.store.ts",
        "components/card/asset-housekeeper/CardAssetHousekeeper.store.ts",
        "components/action-bar/scheduled-work-mixin/ActionBarScheduledWorkMixin.store.ts",
        "components/table/assets/TableAssets.store.ts",
        "components/select/building/SelectBuilding.vue"
    ],
    "@pedromcosta": [
        "store/root/Root.store.ts"
    ],
    "Orphaned files": [
        "views/utilities/ScreenUtilities.store.ts",
        "components/side-dialog/other-cost/SideDialogOtherCost.store.ts",
        "components/side-dialog/utility-type/SideDialogUtilityType.store.ts",
        "components/side-dialog/material/SideDialogMaterial.store.ts",
        "components/side-dialog/cost-center/SideDialogCostCenter.store.ts",
        "components/account/settings/AccountSettings.store.ts",
        "components/account/notifications/AccountNotifications.store.ts",
        "components/account/general/AccountGeneral.store.ts",
        "components/select/warehouse/SelectWarehouse.vue"
    ]
}


def run():

    repo_path = None
    verbose = False
    copy_to_clipboard = False
    format_for_gitlab = False
    args = []

    match sys.argv:
        case [_]:
            print('Empty repository path')
            exit(1)
        case [_, path]:
            repo_path = path
        case [_, path, *args]:
            repo_path = path
            args = args

    verbose = '-v' in args
    copy_to_clipboard = '--copy' in args
    format_for_gitlab = '--gitlab' in args

    src_path = str(Path(f'{repo_path}/src').expanduser())

    codeowners_file = Path(f'{repo_path}/CODEOWNERS').expanduser()

    rg = Ripgrepy("expanded: [',\\[].*", src_path)

    files_to_refactor = rg.files_with_matches().run().as_string

    lines = files_to_refactor.split('\n')

    # We're ignoring test files because they are most likely testing API calls
    # whenever a 'expanded: ' match is found
    file_paths = [f.replace(src_path+'/', '')
                  for f in lines
                  if f != ''
                  and not f.endswith('spec.ts')]

    # PARSE CODEOWNERS FILE
    codeowners = None

    try:
        with codeowners_file.open() as f:
            codeowners = CodeOwners(f.read())
    except IOError:
        print(f'Cannot find a CODEOWNERS file '
              f'are you sure WebCoreClient is located in {repo_path}')
        exit(1)

    # ASSIGN EACH FILE TO A TEAM

    team_assignments = {}

    for file_to_refactor in file_paths:
        teams = codeowners.of('src/'+file_to_refactor)
        teams = [t[1] for t in teams]
        if not teams:
            teams = ['Orphaned files']
        for team in teams:
            assigned_files = team_assignments.get(team, [])
            team_assignments[team] = assigned_files + [file_to_refactor]

    # PRINT FILES AND STATS

    team_names = []
    percentages = []

    baseline_file_counts = {k: len(v) for k, v in team_baselines.items()}
    baseline_file_names = {k: v for k, v in team_baselines.items()}
    file_status_list = {}

    report_lines = []

    for team, files_to_fix in sorted(team_assignments.items()):
        pending = len(files_to_fix)
        baseline = baseline_file_counts[team]
        pct_done = round((1-(pending / baseline))*100, 0)
        fixed_string = f'fixed {baseline - pending} of {baseline} files'

        # Get the team name only
        result = re.search(r"@infraspeak/.*/(.*)/.*", team)
        if result:
            team_name = result.group(1)
        else:
            team_name = team
        team_names.append(f'{team_name} {baseline - pending}/{baseline}')

        percentages.append(pct_done)

        file_items = [[file, file in files_to_fix]
                      for file in sorted(baseline_file_names.get(team, ''))]

        if verbose:
            percent_done_by_team = f'{pct_done}% DONE ({fixed_string})'
            report_lines.append(f'{team} {percent_done_by_team}')

            tab_character = '  '

            # if format_for_gitlab:
            #     tab_character = '&emsp;'

            for file_item in sorted(file_items):
                file_name = file_item[0]
                if file_item[1]:
                    report_lines.append(f'{tab_character}❌ {file_name}')
                    file_status_list[file_name] = False
                else:
                    report_lines.append(f'{tab_character}✅ {file_name}')
                    file_status_list[file_name] = True
        else:
            for file_item in sorted(file_items):
                file_name = file_item[0]
                if file_item[1]:
                    file_status_list[file_name] = False
                else:
                    file_status_list[file_name] = True

    # REPORT TEXT

    report_text = "\n".join(report_lines)

    if format_for_gitlab:
        report_text = f"""
<p>
<details>
<summary>Click for detailed file list</summary>
<pre>
{report_text}
</pre>
</details>
</p>
        """

    # OVERALL STATS

    fixed_files_count = len(
        [f for f in file_status_list.values() if f is True])
    total_file_count = len(list(file_status_list.items()))

    percent_done = (fixed_files_count / total_file_count)*100

    title = f'OVERALL REFACTORING STATUS {percent_done:.2f}%'

    # BY TEAM STATS

    plt.simple_bar(team_names, percentages, width=75,
                   title=title)
    plt.show()

    # PRINT FILE LIST

    print()

    print(report_text)

    if (copy_to_clipboard):
        if format_for_gitlab:
            # strip ANSI color escape codes from string before copying to clipboard
            text_plot = str(f'<pre>{plt.uncolorize(plt.build())}</pre>')
        else:
            text_plot = str(f'{plt.uncolorize(plt.build())}\n')
        report_text = text_plot + report_text
        pyperclip.copy(report_text)


if __name__ == '__main__':
    run()
