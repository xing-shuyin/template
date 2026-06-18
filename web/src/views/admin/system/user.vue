<template>
    <div class="main">
        <div class="main-top">
            <div class="search">
                <!-- <f-input v-model="form.label" label="名称" /> -->
                <f-input v-model="filter.name__contains" label="名称" />
            </div>
            <div class="tool">
                <el-button circle @click="attrs.current_show = true; attrs.current = {}; attrs.current_type = 'add'">
                    <Icon icon="ep:plus" class="btn-icon" />
                </el-button>
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base"></f-columns-edit>
            </div>
        </div>
        <div class="main-table">
            <el-table :data="attrs.data" style="width: 100%;height: 100%;">
                <columns :columns="attrs.columns"></columns>
                <el-table-column label="操作" width="180" align="center">
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
                <el-form-item label="名称" prop="fullname">
                    <el-input v-model="attrs.current.fullname" />
                </el-form-item>
                <el-form-item label="激活" prop="is_active">
                    <el-switch v-model="attrs.current.is_active" />
                </el-form-item>
                <el-form-item label="超级用户" prop="is_superuser">
                    <el-switch v-model="attrs.current.is_superuser" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="attrs.current.email" />
                </el-form-item>
                <el-form-item label="父级部门" prop="dept_id">
                    <el-cascader v-model="attrs.current.dept_id" :options="attrs.depts" clearable
                        :props="{ emitPath: false, checkStrictly: true, value: 'id', label: 'name', }" />
                </el-form-item>

                <el-form-item label="角色" prop="roles">
                    <el-select v-model="attrs.current.roles" multiple placeholder="角色" style="width: 240px">
                        <el-option v-for="item in attrs.roles" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
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
    base: 'user',
    data: [],
    current: {},
    current_show: false,
    current_type: 'add',
    total: 0,
    columns: [
        { type: 'text', width: 180, label: '名称', prop: 'fullname', align: "center", show: true, },
        { type: 'bool', width: 180, label: '激活', prop: 'is_active', align: "center", show: true, },
        { type: 'bool', width: 180, label: '超级用户', prop: 'is_superuser', align: "center", show: true, },
        { type: 'text', width: 180, label: '邮箱', prop: 'email', align: "center", show: true, },
        { type: 'text', width: 180, label: '部门', prop: 'dept__name', align: "center", show: true, },
        { type: 'list_item', width: 180, label: '角色', prop: 'roles', align: "center", show: true, option: {} },
        { type: 'text', width: 180, label: '创建时间', prop: 'created_at', align: "center", show: true, },
        { type: 'text', width: 180, label: '更新时间', prop: 'updated_at', align: "center", show: true, },
    ]
})
const form = ref(null)
const rules = reactive({
    name: [
        { required: true, message: '请填写名称', trigger: 'blur' },
    ],
})
const filter = reactive({
    limit: 10,
    page: 1,
    extra: ['dept__name']
})
watch(filter, () => {
    get_data()
});
const special_filter = reactive({
    range: [],
});



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
        attrs.total = parseInt(res.total)
    })
}
get_data()

r.get('/dept/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    attrs.depts = Tree(res.data, 'id', 'parent_id')
})
r.get('/role/', { params: { page: 1, limit: 99999 } }).then(res => {
    res = res.data
    attrs.roles = res.data
    attrs.columns.forEach(i => {
        if (i.prop == 'roles') {
            i.option = attrs.roles.reduce((pre, cur) => {
                pre[cur.id] = cur.name
                return pre
            }, {})
        }

    });
    console.log(attrs.columns);

})

</script>
<style lang="scss"></style>