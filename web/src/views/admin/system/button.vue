<template>
    <div class="main">
        <div class="main-top">
            <div class="search">
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
            <el-table :data="attrs.data" style="width: 100%;height: 100%;" stripe @sort-change="sort">
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
            :modal="false">
            <el-form :model="attrs.current" label-width="120px" ref="form" :rules="rules">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="attrs.current.name" placeholder="按钮显示名称" />
                </el-form-item>
                <el-form-item label="权限标识" prop="code">
                    <el-input v-model="attrs.current.code" placeholder="如 user:add, role:delete" />
                </el-form-item>
                <el-form-item label="所属菜单">
                    <el-select v-model="attrs.current.menu_id" placeholder="选择菜单" clearable filterable>
                        <el-option v-for="m in menus" :key="m.id" :label="m.label" :value="m.id" />
                    </el-select>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="attrs.current_show = false">取消</el-button>
                    <el-button type="primary" @click="validate">提交</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import r from '@/utils/request'
import { Icon } from '@iconify/vue'

const attrs = reactive({
    base: 'button',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'text', width: 'auto', label: '名称', prop: 'name', align: "center", show: true },
        { type: 'text', width: 'auto', label: '权限标识', prop: 'code', align: "center", show: true },
        { type: 'text', width: 180, label: '创建时间', prop: 'created_at', align: "center", show: true, sortable: true },
        { type: 'text', width: 180, label: '更新时间', prop: 'updated_at', align: "center", show: true, sortable: true },
    ],
})
const form = ref(null)
const rules = reactive({
    name: [{ required: true, message: '请填写名称', trigger: 'blur' }],
    code: [{ required: true, message: '请填写权限标识', trigger: 'blur' }],
})
const filter = reactive({ limit: 100, page: 1 })
const menus = ref([])

watch(filter, () => { get_data() })

const sort = (d) => {
    if (d.order == 'ascending') filter.order = d.prop
    else if (d.order == 'descending') filter.order = '-' + d.prop
    else filter.order = ''
}

const validate = () => {
    form.value.validate((valid, fields) => {
        if (valid) { submit() }
        else {
            ElMessage({ showClose: true, message: Object.values(fields)[0][0]['message'], center: true })
        }
    })
}

const del = (row) => {
    r.delete(`/${attrs.base}/${row.id}`).then(res => {
        if (res.status == 200) ElMessage({ message: '删除成功', type: 'success', plain: true })
        get_data()
    })
}

const edit = (row) => {
    attrs.current_show = true
    attrs.current_type = 'edit'
    attrs.current = { ...row }
}

const submit = () => {
    delete attrs.current.created_at
    delete attrs.current.updated_at
    if (attrs.current_type == 'add') {
        r.post(`/${attrs.base}/`, attrs.current).then(res => {
            if (res.status == 200) {
                ElMessage({ message: '添加成功', type: 'success', plain: true })
                attrs.current_show = false
                get_data()
            }
        })
    } else {
        if (attrs.current.id) {
            r.patch(`/${attrs.base}/${attrs.current.id}`, attrs.current).then(res => {
                if (res.status == 200) {
                    ElMessage({ message: '修改成功', type: 'success', plain: true })
                    attrs.current_show = false
                    get_data()
                }
            })
        }
    }
}

const get_data = () => {
    attrs.data = []
    r.get(`/${attrs.base}/`, { params: filter }).then(res => {
        res = res.data
        attrs.data = res.data || []
        attrs.total = parseInt(res.total)
    })
}
get_data()

r.get('/menu/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    menus.value = res.data || []
})
</script>
<style lang="scss" scoped></style>
