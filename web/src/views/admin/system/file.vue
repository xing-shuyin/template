<template>
    <div class="main">
        <div class="main-top">
            <div class="search">
                <f-input v-model="filter.name__contains" label="名称: " placeholder="请输入名称" />
            </div>
            <div class="tool">
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base"></f-columns-edit>
            </div>
        </div>
        <div class="main-table">
            <el-table :data="attrs.data" style="width: 100%;height: 100%;" stripe @sort-change="sort">>
                <columns :columns="attrs.columns"></columns>
                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #default="scope">
                        <el-popconfirm title="确定删除吗?" @confirm="del(scope.row)">
                            <template #reference>
                                <el-button type="danger" link>删除</el-button>
                            </template>
                        </el-popconfirm>

                    </template>
                </el-table-column>
            </el-table>
        </div>
        <div class="main-foot">
            <el-pagination background layout="prev, pager, next" hide-on-single-page style="margin: 5px;"
                :total="attrs.total" :page-sizes="[10, 20, 30, 40]" v-model:page-size="filter.limit"
                v-model:current-page="filter.page" />
        </div>
    </div>
</template>
<script setup>
import r from '@/utils/request'
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue
const attrs = reactive({
    base: 'file',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'file', width: 'auto', label: '名称', prop: 'name', align: "center", show: true, },
        { type: 'text', width: 180, label: '大小', prop: 'size', align: "center", show: true, },
        { type: 'text', width: 180, label: '类型', prop: 'type', align: "center", show: true, },
        { type: 'text', width: 180, label: '创建时间', prop: 'created_at', align: "center", show: true, sortable: true },
        { type: 'text', width: 180, label: '更新时间', prop: 'updated_at', align: "center", show: true, sortable: true },
    ]
})
const filter = reactive({
    limit: 100,
    page: 1,
})
const special_filter = reactive({
    range: [],
});
watch(filter, () => {
    get_data()
});


const sort = (d) => {
    if (d.order == 'ascending') {
        filter.order = d.prop
    } else if (d.order == 'descending') {
        filter.order = '-' + d.prop
    } else {
        filter.order = ''
    }
};


const del = (row) => {
    r.delete(`/${attrs.base}/${row.id}`).then(res => {
        console.log(res);
        if (res.status == 200)
            ElMessage({
                message: '删除成功',
                type: 'success',
                plain: true,
            })
        get_data()
    })
};


const get_data = (append = false) => {
    attrs.data = []
    r.get(`/${attrs.base}/`, { params: filter }).then(res => {
        res = res.data
        attrs.data = res.data || []
        attrs.total = parseInt(res.total)
    })
}
get_data()
</script>
<style lang="scss" scoped></style>