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
            <el-table :data="attrs.data" style="width: 100%;height: 100%;" stripe @sort-change="sort">>
                <columns :columns="attrs.columns"></columns>
                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" link @click="get_permission(scope.row)">权限</el-button>
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
                <el-form-item label="名称" prop="name">
                    <el-input v-model="attrs.current.name" />
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





        <el-drawer v-model="attrs.permissions_show" title="角色权限" size="50%" center close-on-click-modal>
            <el-select v-model="attrs.current.permission" placeholder="权限范围">
                <el-option v-for="v, k in permission_type" :key="parseInt(k)" :label="v" :value="parseInt(k)" />
            </el-select>
            <h3 style="margin-top: 20px;">接口权限</h3>
            <div class="permissions-body common-scroll">
                <el-transfer v-model="attrs.current.interfaces" :data="attrs.interfaces" :titles="['未授权', '已授权']"
                    :props="{
                        key: 'id',
                        label: 'name',
                    }" />
            </div>
            <el-divider />
            <h3>按钮权限</h3>
            <el-transfer v-model="attrs.current.buttons" :data="attrs.buttons" :titles="['未授权', '已授权']"
                :props="{
                    key: 'id',
                    label: 'name',
                }" />
            <el-divider />
            <h3>菜单权限</h3>
            <el-tree ref="menu_tree" :data="attrs.menus" node-key="id" show-checkbox check-strictly default-expand-all>
                <template #default="{ node, data }">
                    <div class="permission-item">
                        <div class="permission-item-label">{{ data.label }}</div>
                    </div>
                </template>
            </el-tree>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="attrs.permissions_show = false">取消</el-button>
                    <el-button type="primary" @click="set_permissions">
                        提交
                    </el-button>
                </span>
            </template>
        </el-drawer>
    </div>

</template>
<script setup>
import r from '@/utils/request'
import { Icon } from '@iconify/vue';  //https://www.npmjs.com/package/@iconify/vue
import { Tree } from '@/utils/tool'
const attrs = reactive({
    base: 'role',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'text', width: 'auto', label: '名称', prop: 'name', align: "center", show: true, },
        { type: 'text', width: 180, label: '创建时间', prop: 'created_at', align: "center", show: true, sortable: true },
        { type: 'text', width: 180, label: '更新时间', prop: 'updated_at', align: "center", show: true, sortable: true },
    ],

    permissions_show: false,
    buttons: [],
})
const form = ref(null)
const menu_tree = ref();
const rules = reactive({
    name: [
        { required: true, message: '请填写名称', trigger: 'blur' },
    ],
})
const permission_type = {
    1: "仅本人数据权限",
    2: "本部门数据权限",
    3: "本部门及以下数据权限",
    4: "不限制部门"
};
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

const validate = () => {
    form.value.validate((valid, fields) => {
        if (valid) {
            submit();
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
    console.log('submit', attrs.current_type);
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
                attrs.permissions_show = false
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
                attrs.permissions_show = false
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
        attrs.total = parseInt(res.total)
    })
}
get_data()

r.get('/interface/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    attrs.interfaces = res.data
})
r.get('/menu/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    attrs.menus = Tree(res.data, 'id', 'parent_id')
})
r.get('/button/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    attrs.buttons = res.data || []
})
const get_permission = (row) => {
    attrs.current_type = 'edit'
    attrs.permissions_show = true
    attrs.current = { ...row }
    console.log('get_permission', attrs.current_type);
    setTimeout(() => {
        menu_tree.value.setCheckedKeys(row.menus, true)
    }, 100);
}
const set_permissions = (row) => {
    attrs.current_type = 'edit'
    attrs.current.menus = menu_tree.value.getCheckedKeys()
    console.log('set_permissions', attrs.current_type);
    submit()
};
</script>
<style lang="scss" scoped></style>