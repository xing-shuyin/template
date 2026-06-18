<template>
    <div class="main">
        <div class="main-top">
            <div class="search">
                <!-- <f-input v-model="form.label" label="名称" /> -->
                <f-input v-model="filter.name__contains" label="名称: " placeholder="请输入名称" />

            </div>
            <div class="tool">
                <el-button circle @click="attrs.current_show = true; attrs.current = {}; attrs.current_type = 'add'">
                    <Icon icon="ep:plus" class="btn-icon" />
                </el-button>
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base"></f-columns-edit>
            </div>
        </div>
        <div class="main-table">
            <el-table :data="attrs.data_tree" style="width: 100%;height: 100%;" row-key="id" default-expand-all stripe
                @sort-change="sort">>
                <columns :columns="attrs.columns"></columns>
                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" link @click="edit(scope.row)">编辑</el-button>
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
        <el-dialog class="admin_detail_dialog" v-model="attrs.current_show" :append-to-body="false" :show-close="false"
            destroy-on-close :modal="false">
            <el-form :model="attrs.current" label-width="120px" ref="form" :rules="rules">
                <el-form-item label="父级部门" prop="parent">
                    <el-cascader v-model="attrs.current.parent_id" :options="attrs.data_tree" clearable
                        :props="{ emitPath: false, checkStrictly: true, value: 'id', label: 'name', }" />
                </el-form-item>
                <el-form-item label="部门名称" prop="name">
                    <el-input v-model="attrs.current.name" />
                </el-form-item>
                <el-form-item label="key" prop="key">
                    <el-input v-model="attrs.current.key" />
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="attrs.current_show = false">取消</el-button>
                    <el-button type="primary" @click="validate">
                        提交
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>

</template>
<script setup>
import r from '@/utils/request'
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue
import { Tree } from '@/utils/tool'
const attrs = reactive({
    base: 'dept',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'text', width: 'auto', label: '名称', prop: 'name', align: "left", show: true, },
        { type: 'text', width: 180, label: 'key', prop: 'key', align: "center", show: true, sortable: true },
        { type: 'text', width: 180, label: '上级部门', prop: 'parent__name', align: "center", show: true, },
        { type: 'text', width: 180, label: '上级部门key', prop: 'parent__key', align: "center", show: true, },
        { type: 'text', width: 180, label: '创建时间', prop: 'created_at', align: "center", show: true, sortable: true },
        { type: 'text', width: 180, label: '更新时间', prop: 'updated_at', align: "center", show: true, sortable: true },
    ]
})
const form = ref(null)
const rules = reactive({
    name: [
        { required: true, message: '请填写部门名称', trigger: 'blur' },
    ],
})
const filter = reactive({
    limit: 100,
    page: 1,
    extra: ['parent__name', 'parent__key']
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

const validate = () => {
    form.value.validate((valid, fields) => {
        if (valid) {
            submit(attrs.base_url, attrs.add_form, attrs.submit_type, get_data);
            attrs.adding = false
        } else {
            ElMessage({
                showClose: true,
                message: Object.values(fields)[0][0]['message'],
                center: true,
            });
        }
    })
}


const add = () => {
    attrs.current_show = true
    attrs.current_type = 'add'
    attrs.current = {}
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
const edit = (row) => {
    console.log(row);
    attrs.current_show = true
    attrs.current_type = 'edit'
    attrs.current = { ...row }
};

const submit = () => {
    delete attrs.current.children
    delete attrs.current.created_at
    delete attrs.current.updated_at
    if (attrs.current_type == 'add') {
        r.post(`/${attrs.base}/`, attrs.current).then(res => {
            console.log(res);
            if (res.status == 200) {
                ElMessage({
                    message: '添加成功',
                    type: 'success',
                    plain: true,
                })
                attrs.current_show = false
                get_data()
            }
        })
    } else {
        if (attrs.current.id) {
            if (attrs.current.parent_id == attrs.current.id) {
                ElMessage({
                    message: '上级部门不能是自身',
                    type: 'error',
                    plain: true,
                })
                return
            }
        }
        r.patch(`/${attrs.base}/${attrs.current.id}`, attrs.current).then(res => {
            console.log(res);
            if (res.status == 200) {
                ElMessage({
                    message: '修改成功',
                    type: 'success',
                    plain: true,
                })
                attrs.current_show = false
                get_data()
            }
        })
    }
};
const get_data = (append = false) => {
    attrs.data = []
    r.get(`/${attrs.base}/`, { params: filter }).then(res => {
        res = res.data
        attrs.data = res.data || []
        attrs.data_tree = Tree(attrs.data, 'id', 'parent_id')
        attrs.total = parseInt(res.total)
    })
}
get_data()
</script>
<style lang="scss" scoped></style>