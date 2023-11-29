<template>
    <is-screen-table
        ref="screen"
        :filters="appliedFilters"
        :column-visibility-options="tableColumnConfigs"
        :columns="toggableTableColumns"
        :refreshing="loadingTable"
        local-storage-key="ScreenWorks"
        class="screen-works"
        data-test="screen-works"
        @main-action-event="createWork"
        @column-visibility-changed="onColumnVisibilityChanged"
        @page-change="onPageChange"
        @search="search"
        @apply-filters="applyFilters"
        @remove-filter="removeFilter"
        @refresh="refresh">
        <template #actionBar>
            <screen-works-action-bar
                :work-id="selectedWorkId"
                @work-responsibles-edited="refresh"
                @work-created="onWorkCreated"
                @work-edited="onWorkEdited"
                @work-duplicated="refresh"
                @work-closed="refresh" />
        </template>
        <template #filterPanel>
            <screen-works-panel-filter
                ref="panelFilter"
                v-model="filters"
                @force-apply-filters="applyFilters" />
        </template>
        <template #default>
            <table-works
                v-if="!isMobile"
                :key="$route.params.state"
                has-pagination
                :pagination-info="paginationInfo"
                :columns="visibleTableColumns"
                :data="tableData"
                :default-sort-field="sortField"
                :default-sort-direction="sortDirection"
                :loading="loadingTable"
                @show-work-info="onShowWorkInfo"
                @work-selected="onSelectWork"
                @sort-change="onSortChange"
                @page-change="onPageChange"
                @column-width-changed="onColumnWidthChanged" />
            <list-card-works
                v-else
                :data="tableData"
                :pagination-info="paginationInfo"
                :loading="loadingTable"
                @show-work-info="onShowWorkInfo"
                @refresh="refresh"
                @page-change="onPageChange" />
        </template>
        <template
            v-if="detailPanelVisible"
            #detailPanel>
            <el-tabs class="screen-works__details">
                <el-tab-pane>
                    <template slot="label">
                        <i class="fal fa-info-circle" />
                        <span>{{ $t('redesign__screen-works.information') }}</span>
                    </template>
                    <info-work
                        :work-id="selectedWorkId"
                        :narrow="true"
                        :has-navigation-menu="false"
                        @update="updateRegistry" />
                </el-tab-pane>
                <el-tab-pane>
                    <template slot="label">
                        <i class="fal fa-history" />
                        <span>{{ $t('redesign__screen-works.history') }}</span>
                    </template>
                    <history-work :work-id="selectedWorkId" />
                </el-tab-pane>
            </el-tabs>
        </template>
    </is-screen-table>
</template>

<script lang="ts">
    import { debounce, filter } from 'lodash'
    import { Component, Vue, Watch } from 'vue-property-decorator'
    import { Route } from 'vue-router'

    import { arrayHelper } from '@/helpers/array/Array.helper'

    import { ListNavigator } from '@/models/list-navigator/ListNavigator.model'
    import { PaginationInfo } from '@/models/pagination-info/PaginationInfo.model'
    import { EnumTableWorkState, Work } from '@/models/work/Work.model'
    import { MenuFilter } from '../home/ScreenHome.types'
    import { EnumTableWorksColumnType } from '@/components/table/works/TableWorks.types'
    import { FilterItem, ITableVisibilityConfig } from '@/components-is/screen-table/IsScreenTable.types'
    import { ITableSort, TableColumn, TableSortOrder, TableSortProp } from '@/components-is/table/IsTable.types'

    import { screenHomeStore } from '../home/ScreenHome.store'
    import { screenWorksStore } from './ScreenWorks.store'
    import { historyWorkStore } from '@/components/history/work/HistoryWork.store'
    import { modalWorkStore } from '@/components/modal/work/ModalWork.store'
    import { modalWorkPageStore } from '@/components/modal/work-page/ModalWorkPage.store'
    import { rootStore } from '@/store/root/Root.store'

    import ScreenWorksActionBar from './components/action-bar/ScreenWorksActionBar.vue'
    import ScreenWorksPanelFilter from './components/panel-filter/ScreenWorksPanelFilter.vue'
    import HistoryWork from '@/components/history/work/HistoryWork.vue'
    import InfoWork from '@/components/info/work/InfoWork.vue'
    import ListCardWorks from '@/components/list-card/works/ListCardWorks.vue'
    import TableWorks from '@/components/table/works/TableWorks.vue'
    import IsScreenTable from '@/components-is/screen-table/IsScreenTable.vue'

    @Component({
        components: {
            IsScreenTable,
            TableWorks,
            ScreenWorksActionBar,
            ScreenWorksPanelFilter,
            ListCardWorks,
            InfoWork,
            HistoryWork,
        },
    })
    export default class ScreenWorks extends Vue {
        $refs!: {
            screen: IsScreenTable
            panelFilter: ScreenWorksPanelFilter
        }

        debounce = debounce((action: Function) => { action() }, 500)
        selectingWork = false
        filters: FilterItem[] = []

        get selectedWorkId (): string | null {
            return screenWorksStore.selectedWorkId
        }

        get detailPanelVisible (): boolean {
            return this.selectedWorkId !== null && !this.$route.query.workId
        }

        get topMenuFilters (): MenuFilter[] {
            return screenWorksStore.topMenuFilters
        }

        get tableData (): Work[] {
            return screenWorksStore.tableData
        }

        get visibleTableColumns (): TableColumn[] {
            return screenWorksStore.visibleTableColumns
        }

        get tableColumnConfigs (): ITableVisibilityConfig | null {
            return screenWorksStore.tableColumnConfigs
        }

        get paginationInfo (): PaginationInfo {
            return screenWorksStore.apiPagination
        }

        get loadingTable (): boolean {
            return screenWorksStore.loading
        }

        get availableTableColumns (): TableColumn[] {
            return screenWorksStore.availableTableColumns
        }

        get toggableTableColumns (): TableColumn[] {
            return filter(this.availableTableColumns, 'canToggleVisibility')
        }

        get sortDirection (): TableSortOrder {
            return screenWorksStore.tableCurrentSortOptions.order
        }

        get sortField (): TableSortProp {
            return screenWorksStore.tableCurrentSortOptions.prop
        }

        get appliedFilters (): FilterItem[] {
            return screenWorksStore.filters
        }

        get isMobile (): boolean {
            return rootStore.isMobile
        }

        created (): void {
            screenWorksStore.setSearch('')
        }

        mounted (): void {
            screenHomeStore.setMenuFilters(this.topMenuFilters)

            this.filters = [...this.appliedFilters]
        }

        @Watch('topMenuFilters')
        onTopMenuFiltersChanged (): void {
            screenHomeStore.setMenuFilters(this.topMenuFilters)
        }

        @Watch('$route.params.state', { immediate: true })
        onRouteStateParamChanged (val?: EnumTableWorkState): Promise<Route> | undefined {
            if (!val) {
                return this.$router.push({ name: 'works', params: { state: 'active' } })
            }

            screenWorksStore.changeTableState(val)

            screenWorksStore.loadTableConfigs(val)

            this.resetPageAndRefresh()
        }

        @Watch('detailPanelVisible')
        onDetailPanelVisible (value: boolean): void {
            if (value) {
                this.$refs.screen.showDetailPanel()
            } else {
                this.$refs.screen.hideDetailPanel()
            }
        }

        beforeDestroy (): void {
            screenHomeStore.setMenuFilters([])
        }

        resetPageAndRefresh (): void {
            this.paginationInfo.reset()

            this.$nextTick(this.refresh)
        }

        onPageChange (page: number): Promise<Work[]> {
            this.paginationInfo.page = page

            return this.refresh()
        }

        onWorkCreated (workId: string): void {
            // Opens modal planned job (work) details when work is successfully created
            modalWorkPageStore.open({ workId })
            this.refresh()
        }

        onWorkEdited (workId: string): void {
            modalWorkPageStore.open({ workId })
            this.refresh()
        }

        createWork (): void {
            modalWorkStore.open({ successCallback: this.onWorkCreated })

            this.$sendAnalyticPageViewEvent('/works/new')
        }

        editWork (): void {
            modalWorkStore.open({ successCallback: this.onWorkEdited })

            this.$sendAnalyticPageViewEvent('/works/edit')
        }

        refresh (): Promise<Work[]> {
            return screenWorksStore.loadTable()
        }

        search (search: string): void {
            screenWorksStore.setSearch(search)

            this.resetPageAndRefresh()
        }

        onSelectWork (work: Work | null): void {
            this.selectingWork = true
            this.debounce(() => {
                screenWorksStore.setSelectedWorkId(work ? work._id : null)

                this.selectingWork = false
            })
        }

        onSortChange (sortOptions: ITableSort): void {
            screenWorksStore.setTableWorksSort(sortOptions)

            this.refresh()
        }

        onColumnVisibilityChanged (configs: any): void {
            screenWorksStore.setTableWorks([])

            screenWorksStore.saveColumnConfigs(configs)

            this.refresh()
        }

        applyFilters (): void {
            screenWorksStore.setFilters(this.filters)

            this.resetPageAndRefresh()
        }

        removeFilter (filter: FilterItem): FilterItem[] | void {
            arrayHelper.removeItems(this.filters, (filterItem: FilterItem) => {
                return filterItem.id === filter.id && filterItem.type === filter.type
            })

            // HACK: If the panel is closed, we need to force the update
            if (this.$refs.panelFilter && this.$refs.screen.filterPanelHidden === true) {
                this.$refs.panelFilter.updateComponent(this.filters)
            }

            this.applyFilters()
        }

        onShowWorkInfo (work: Work): void {
            modalWorkPageStore.open({
                workId: work._id,
                listNavigator: new ListNavigator({
                    currentItemId: work._id,
                    currentList: this.tableData,
                    pagination: this.paginationInfo,
                    loadList: this.onPageChange,
                }),
            })
        }

        onColumnWidthChanged (width: number, column: EnumTableWorksColumnType): void {
            if (this.tableColumnConfigs?.configs[column]) {
                this.tableColumnConfigs.configs[column].width = width
                screenWorksStore.saveColumnConfigs(this.tableColumnConfigs)
            }
        }

        updateRegistry (): void {
            historyWorkStore.loadWorkRegistry()
        }
    }
</script>

<style lang="scss">
    .screen-works {
        &__details {
            height: 100%;
            .el-tabs__content {
                height: calc(100% - 40px);
                padding: 0;
                .el-tab-pane {
                    height: 100%;
                }
            }
        }
    }
</style>
