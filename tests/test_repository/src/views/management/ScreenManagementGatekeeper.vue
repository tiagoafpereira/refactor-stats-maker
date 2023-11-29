<template>
    <div class="content-max-width--settings">
        <div class="screen-management-gatekeeper">
            <div data-test="screen-management-gatekeeper_title-container">
                <h2 class="pk-display-small mb-small">
                    {{ $t('redesign__screen-management-gatekeeper.title') }}
                </h2>
                <p>{{ $t('redesign__screen-management-gatekeeper.description') }}</p>
            </div>

            <pk-card class="screen-management-gatekeeper__create-checklist">
                <p class="pk-body-body-bold">
                    {{ $t('redesign__screen-management-gatekeeper.create-customised-checklists') }}
                </p>
                <pk-button
                    :label="$t('redesign__action-bar-gatekeeper.checklist-create')"
                    icon="pkicon pkicon-16 pkicon-light pkicon-plus"
                    data-test="screen-management-gatekeeper_create-checklist"
                    @click="createGatekeeper" />
            </pk-card>

            <is-list
                v-loading="loading"
                :list="gatekeepers"
                :pagination-info="pagination"
                :num-to-display="pagination.itemsPerPage"
                data-test="screen-management-gatekeeper_list">
                <template #default="{item: gatekeeper}">
                    <is-card-navigation
                        :key="gatekeeper._id"
                        :description="gatekeeper.description"
                        :title="`${gatekeeper._id} - ${gatekeeper.name}`"
                        show-new-layout
                        @click.native="editGatekeeper(gatekeeper._id)">
                        <!-- TODO: CFT-1843 -->
                        <!-- <template #title>
                            <pk-object-gatekeeper
                                size="x-small"
                                :code="gatekeeper._id"
                                :description="gatekeeper.name" />
                        </template> -->
                        <template #right>
                            <div
                                :title="$t('redesign__table-gatekeeper.number-of-checklist-and-files', { files: gatekeeper.files.length, checklist: gatekeeper.checklist.length })"
                                class="screen-management-gatekeeper__icons">
                                <span>{{ gatekeeper.checklist.length }}<i class="pkicon pkicon-16 pkicon-light pkicon-gatekeeper-checklist" /></span>
                                <span>{{ gatekeeper.files.length }}<i class="pkicon pkicon-16 pkicon-light pkicon-attachment" /></span>
                            </div>
                        </template>
                    </is-card-navigation>
                </template>
            </is-list>
        </div>
    </div>
</template>

<script lang="ts">
    import { defineComponent } from 'vue'

    import { gatekeeperApi } from '@/api/gatekeeper.api'

    import { CancelableRequest } from '@/helpers/loading/Loading.helper'

    import { Gatekeeper } from '@/models/gatekeeper/Gatekeeper.model'
    import { PaginationInfo } from '@/models/pagination-info/PaginationInfo.model'

    import { sideDialogGatekeeperChecklistStore } from '@/components/side-dialog/gatekeeper-checklist/SideDialogGatekeeperChecklist.store'

    import IsCardNavigation from '@/components-is/card-navigation-new/IsCardNavigationNew.vue'
    import IsList from '@/components-is/list/IsList.vue'
    import PkButton from '@/pocketknife/components/button/PkButton.vue'
    import PkCard from '@/pocketknife/components/card/PkCard.vue'

    type Data = {
        readonly cancelableRequest: CancelableRequest
        pagination: PaginationInfo
        gatekeepers: Gatekeeper[]
    }

    export default defineComponent({
        name: 'ScreenManagementGatekeeper',

        components: {
            IsCardNavigation,
            IsList,
            PkButton,
            PkCard,
        },

        data (): Data {
            return {
                cancelableRequest: new CancelableRequest(),
                pagination: new PaginationInfo(6),
                gatekeepers: [],
            }
        },

        computed: {
            loading (): boolean {
                return this.cancelableRequest.loading
            },
        },

        watch: {
            'pagination.page': {
                handler: 'onPaginationPageChanged',
            },
        },

        created (): void {
            this.loadGatekeepers()
        },

        methods: {
            loadGatekeepers (): Promise<void> {
                try {
                    return this.cancelableRequest.load(async cancelToken => {
                        const response = await gatekeeperApi.getGatekeepers(
                            {
                                limit: this.pagination.itemsPerPage,
                                page: this.pagination.page,
                                expand: {
                                    files: {},
                                    gatekeeperQuestions: {},
                                },
                            },
                            { cancelToken })

                        this.gatekeepers = response.data
                        this.pagination.update(response.links!)
                    })
                } catch (error) {
                    throw new Error(`Error on loading gatekeepers ${error}`)
                }
            },
            createGatekeeper (): void {
                sideDialogGatekeeperChecklistStore.open({
                    successCallback: this.loadGatekeepers,
                })

                this.$sendAnalyticEvent('click', 'gatekeeper_new')
            },
            editGatekeeper (gatekeeperId: string): void {
                sideDialogGatekeeperChecklistStore.open({
                    gatekeeperId,
                    successCallback: this.loadGatekeepers,
                })
            },
            onPaginationPageChanged (): void {
                this.loadGatekeepers()
            },
        },
    })
</script>

<style lang="scss">
    .screen-management-gatekeeper {
        display: flex;
        flex-direction: column;
        gap: var(--pk-spacing-600);
        padding: var(--pk-spacing-400);

        .pk-card__content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        &__icons {
            display: flex;
            align-items: center;
            gap: var(--pk-spacing-100);

            span {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                min-width: 40px;
                gap: 2px;
            }
        }
    }
</style>
